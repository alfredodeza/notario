import sys
from notario.exceptions import Invalid, SchemaError
from notario.utils import (is_callable, sift, is_empty, re_sort, is_not_empty,
                           data_item, safe_repr, ensure)
from notario.normal import Data, Schema


class Validator(object):

    def __init__(self, data, schema):
        self.data = Data(data, schema).normalized()
        self.schema = Schema(data, schema).normalized()

    def validate(self):
        if self.data == {} and self.schema:
            msg = 'has no data to validate against schema'
            reason = 'an empty dictionary object was provided'
            raise Invalid(None, {}, msg=msg, reason=reason, pair='value')
        self.traverser(self.data, self.schema, [])

    def traverser(self, data, schema, tree):
        """
        Traverses the dictionary, recursing onto itself if
        it sees appropriate key/value pairs that indicate that
        there is a need for more validation in a branch below us.
        """
        if hasattr(schema, '__validator_leaf__'):
            return schema(data, tree)

        if hasattr(schema, 'must_validate'):  # cherry picking?
            if not len(schema.must_validate):
                reason = "must_validate attribute must not be empty"
                raise SchemaError(data, tree, reason=reason)
            data = sift(data, schema.must_validate)

        schema = self.sanitize_optionals(data, schema, tree)

        validated_indexes = []
        skip_missing_indexes = getattr(schema, 'must_validate', False)

        if len(data) < len(schema):
            # we have missing required items in data, but we don't know
            # which ones so find what may fail:
            data_keys = [v[1] for v in data.values()]
            schema_keys = [v[1] for v in schema.values()]

            def enforce_once(data_keys, schema_key):
                # XXX Go through all the data keys and try and see if they pass
                # validation against the schema. At this point it is impossible
                # to know which data key corresponds to what schema key
                # (because schema keys can be a function/callable) so it is
                # a *very* naive way to try and detect which one might be
                # missing
                for data_key in data_keys:
                    failed = None
                    try:
                        enforce(data_key, schema_key, tree, pair='key')
                        return
                    except Invalid:
                        failed = data_key, schema_key

                    if failed:
                        return failed

            for schema_key in schema_keys:
                failure = enforce_once(data_keys, schema_key)
                if failure:
                    _, failed_schema_key = failure
                    msg = "required key in data is missing: %s" % str(failed_schema_key)
                    raise Invalid(None, tree, reason=msg, pair='key')

        for index in range(len(data)):
            self.length_equality(data, schema, index, tree)
            key, value = data[index]
            skey, svalue = schema[index]
            tree.append(key)

            # Validate the key before anything, to prevent recursing
            self.key_leaf(data[index], schema[index], tree)

            # If a dict is a value we need to recurse.
            # XXX Should we check isinstance(value, ndict) ?
            if isinstance(value, dict) and len(value):
                self.traverser(value, svalue, tree)
            else:
                self.value_leaf(data[index], schema[index], tree)
            if tree:
                tree.pop()

            validated_indexes.append(index)

        # XXX There is a chance we might have missing items from
        # the incoming data that are labeled as required from the schema
        # we should make sure *here* that we account for that and raise
        # the appropriate exception. Since the loop finished and everything
        # seems to have passed, this lack of check will give false positives.
        missing_indexes = set(schema.keys()).difference(validated_indexes)
        if missing_indexes:
            if skip_missing_indexes:
                return
            for i in missing_indexes:
                if not hasattr(schema[i], 'is_optional'):
                    required_key = schema[i][0]
                    tree.append('item[%s]' % i)
                    msg = "required item in schema is missing: %s" % str(required_key)
                    raise Invalid(required_key, tree, reason=msg, pair='key')


    def key_leaf(self, data, schema, tree):
        """
        The deepest validation we can make in any given circumstance for a key.
        Does not recurse, it will just receive both values and the tree,
        passing them on to the :fun:`enforce` function.
        """
        key, value = data
        schema_key, schema_value = schema
        enforce(key, schema_key, tree, 'key')

    def value_leaf(self, data, schema, tree):
        """
        The deepest validation we can make in any given circumstance for
        a value. Does not recurse, it will just receive both values and the
        tree, passing them on to the :fun:`enforce` function.
        """
        key, value = data
        schema_key, schema_value = schema

        if hasattr(schema_value, '__validator_leaf__'):
            return schema_value(value, tree)
        enforce(value, schema_value, tree, 'value')

    def length_equality(self, data, schema, index, tree):
        try:
            data = data[index]
            try:
                schema = schema[index]
            except KeyError:
                if not hasattr(schema, 'must_validate'):
                    reason = 'has unexpected item in data: %s' % data_item(data)
                    raise Invalid(None, tree, msg=reason, reason=reason, pair='value')
        except (KeyError, TypeError):
            if not hasattr(schema, 'must_validate'):
                reason = "has less items in schema than in data"
                raise SchemaError(data, tree, reason=reason)
        if hasattr(schema, '__validator_leaf__'):
            return

        if len(data) != len(schema):
            raise SchemaError(data, tree, reason='length did not match schema')

    def sanitize_optionals(self, data, schema, tree):
        schema_key_map = {}
        try:
            for number, value in schema.items():
                schema_key_map[number] = getattr(value[0], '_object', value[0])
        except AttributeError:  # maybe not a dict?
            self.length_equality(data, schema, 0, tree)

        optional_keys = {}
        for k, v in schema.items():
            try:
                key = getattr(v[0], '_object')
                if key:
                    optional_keys[k] = key
            except AttributeError:
                pass

        data_keys = [v[0] for k, v in data.items()]

        for number, value in optional_keys.items():
            if value not in data_keys:
                del schema[number]
        if not schema and is_not_empty(data):
            msg = "unexpected extra items"
            raise Invalid(schema, tree, reason=msg)
        return re_sort(schema)


class BaseItemValidator(object):

    def __init__(self, data, schema, tree=None, index=None, name=None):
        self.data = data
        self.schema = schema
        self.tree = tree or []
        self.index = index or 0
        self.name = name

    def validate(self):
        self.traverser(self.data, self.schema, self.tree)

    def traverser(self, data, schema, tree):
        if len(data) < self.index:
            reason = "has not enough items to select from"
            raise SchemaError(data, tree, reason=reason)
        self.leaves(data, schema, tree)


class IterableValidator(BaseItemValidator):
    """
    The iterable validator allows the definition of a single schema that can be
    run against any number of items in a given data structure
    """

    def data_sanity(self, data, tree=None):
        if not isinstance(data, list):
            name = self.name or 'IterableValidator'
            reason = 'expected a list but got %s' % safe_repr(data)
            msg = 'did not pass validation against callable: %s' % name
            raise Invalid('', tree or [], msg=msg, reason=reason, pair='value')

    def leaf(self, index):
        self.data_sanity(self.data, tree=self.tree)
        self.enforce(self.data, self.schema, index, self.tree)

    def leaves(self, data, schema, tree):
        self.data_sanity(data, tree=tree)
        for item_index in range(self.index, len(data)):
            self.enforce(data, schema, item_index, tree)

    def enforce(self, data, schema, item_index, tree):
        # yo dawg, a recursive validator within a recursive validator anyone?
        if is_callable(schema) and hasattr(schema, '__validator_leaf__'):
            return schema(data[item_index], tree)
        if isinstance(data[item_index], dict) and isinstance(schema, tuple):
            try:
                _validator = Validator(data[item_index], schema)
                _validator.validate()
            except Invalid:
                e = sys.exc_info()[1]
                tree.append('list[%s]' % item_index)
                tree.extend(e.path)
                raise Invalid(e.schema_item, tree, reason=e._reason, pair='value')

            # FIXME this is utterly redundant, and also happens in
            # RecursiveValidator
            except SchemaError:
                e = sys.exc_info()[1]
                tree.extend(e.path)
                raise SchemaError('', tree, reason=e._reason, pair='value')

        elif isinstance(schema, tuple) and not isinstance(data[item_index], (tuple, dict)):
            raise SchemaError(data, tree, reason='iterable contains single items, schema does not')
        else:
            try:
                if is_callable(schema):
                    schema(data[item_index])
                else:
                    ensure(data[item_index] == schema)
            except AssertionError:
                reason = sys.exc_info()[1]
                tree.append('list[%s]' % item_index)
                raise Invalid(schema, tree, reason=reason, pair='item')


class RecursiveValidator(BaseItemValidator):
    """
    The recursive validator allows the definition of a single schema that can
    be run against any number of items in a given data structure
    """

    def leaf(self, index):
        self.enforce(self.data, self.schema, index, self.tree)

    def leaves(self, data, schema, tree):
        for item_index in range(self.index, len(data)):
            self.enforce(data, schema, item_index, tree)

    def enforce(self, data, schema, item_index, tree):
        # yo dawg, a recursive validator within a recursive validator anyone?
        if is_callable(schema) and hasattr(schema, '__validator_leaf__'):
            return schema(data, tree)
        try:
            _validate = Validator({}, self.schema)
            _validate.data = {0: data[item_index]}
            _validate.validate()
        except Invalid:
            e = sys.exc_info()[1]
            tree.extend(e.path)
            raise Invalid(e.schema_item, tree, pair='value', msg=e._msg, reason=e._reason)
        except SchemaError:
            e = sys.exc_info()[1]
            tree.extend(e.path)
            raise SchemaError('', tree, reason=e._reason, pair='value')


def enforce(data_item, schema_item, tree, pair):
    schema_is_optional = hasattr(schema_item, 'is_optional')
    if is_callable(schema_item) and not schema_is_optional:
        try:
            schema_item(data_item)
        except AssertionError:
            e = sys.exc_info()[1]
            if pair == 'value':
                tree.append(data_item)
            raise Invalid(schema_item, tree, reason=e, pair=pair)
    else:
        try:
            if schema_is_optional:
                if is_empty(data_item):  # we received nothing here
                    return
                ensure(data_item == schema_item())
            else:
                ensure(data_item == schema_item)
        except AssertionError:
            e = sys.exc_info()[1]
            if pair == 'value':
                tree.append(data_item)
            raise Invalid(schema_item, tree, reason=e, pair=pair)


def validate(data, schema):
    """
    Main entry point for the validation engine.

    :param data: The incoming data, as a dictionary object.
    :param schema: The schema from which data will be validated against
    """
    if isinstance(data, dict):
        validator = Validator(data, schema)
        validator.validate()
    else:
        raise TypeError('expected data to be of type dict, but got: %s' % type(data))
