import copy
import logging

from atomicapp.constants import (GLOBAL_CONF,
                                 LOGGER_COCKPIT,
                                 DEFAULT_PROVIDER,
                                 NAMESPACE_SEPARATOR)
from collections import defaultdict

cockpit_logger = logging.getLogger(LOGGER_COCKPIT)


class Config(object):
    """
    Store config data for a Nulecule or Nulecule component.
    """

    def __init__(self, namespace='', answers=None, cli=None,
                 data=None, is_nulecule=False):
        self._namespace = namespace
        self._is_nulecule = is_nulecule or False
        self._parent_ns, self._current_ns = self._split_namespace(self._namespace)
        self._answers = defaultdict(dict)
        self._answers.update(answers or {})
        self._cli = cli or {}
        self._data = data or defaultdict(dict)
        self._context = None
        self._provider = None

    @property
    def provider(self):
        """
        Get provider name.

        Returns:
            Provider name (str)
        """
        if self._provider is None:
            self._provider = self._answers[GLOBAL_CONF].get('provider')
            if self._provider is None:
                self._data[GLOBAL_CONF]['provider'] = DEFAULT_PROVIDER
                self._provider = DEFAULT_PROVIDER

        return self._provider

    @property
    def providerconfig(self):
        """
        Get provider config info taking into account answers and cli data.
        """
        pass

    @property
    def namespace(self):
        """
        Get normalized namespace for this instance.

        Returns:
            Current namespace (str).
        """
        return self._namespace or GLOBAL_CONF

    def set(self, key, value):
        self._data[self.namespace][key] = value

    def get(self, key):
        return (
            self._data[self.namespace].get(key) or
            (self._data[self._parent_ns].get(key) if self._parent_ns else None) or
            self._data[GLOBAL_CONF].get(key) or
            self._answers[self.namespace].get(key) or
            (self._answers[self._parent_ns].get(key) if self._parent_ns else None) or
            self._answers[GLOBAL_CONF].get(key)
        )

    def context(self):
        """
        Get context to render artifact files in a Nulecule component.
        """
        if self._context is None:
            self._context = {}
            self._context.update(copy.copy(self._data[GLOBAL_CONF]))
            self._context.update(copy.copy(self._data[self.namespace]))

            self._context.update(copy.copy(self._answers[GLOBAL_CONF]))
            self._context.update(copy.copy(self._answers[self.namespace]))
        return self._context

    def runtime_answers(self):
        """
        Get runtime answers.
        """
        answers = defaultdict(dict)
        answers.update(copy.copy(self._answers))
        for key, value in self._data.items():
            answers[key].update(value)
        return answers

    def clone(self, namespace):
        """
        Create a new config instance in the specified namespace.

        Args:
            name (str): Name of the child component

        Returns:
            A Config instance.
        """
        config = Config(namespace=namespace,
                        answers=self._answers,
                        cli=self._cli,
                        data=self._data)
        return config

    def _split_namespace(self, namespace):
        """
        Split namespace to get parent and current namespace in a Nulecule.
        """
        if self._is_nulecule:
            return '', namespace
        words = namespace.rsplit(NAMESPACE_SEPARATOR, 1)
        parent, current = '', ''
        if len(words) == 2:
            parent, current = words[0], words[1]
        else:
            parent, current = '', words[0]
        return parent, current

    def __eq__(self, obj):
        """
        Check equality of config instances.
        """
        if self._namespace == obj._namespace or self._answers == obj._answers or self._data == obj._data or self._cli == obj._cli:
            return True
        return False
