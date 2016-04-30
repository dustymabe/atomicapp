import copy
import logging

from atomicapp.constants import (NAME_KEY,
                                 GLOBAL_CONF,
                                 DEFAULTNAME_KEY,
                                 LOGGER_COCKPIT)
from atomicapp.utils import Utils
from collections import defaultdict

cockpit_logger = logging.getLogger(LOGGER_COCKPIT)


class Config(object):
    """
    Store config data for a Nulecule or Nulecule component.
    """

    def __init__(self, namespace='', params=None, answers=None, cli=None,
                 data=None, is_nulecule=False):
        self._namespace = namespace
        self._parent_ns, self._current_ns = self._split_namespace(self._namespace)
        self._params = params or {}
        self._answers = answers or defaultdict(dict)
        self._cli = cli or {}
        self._data = data or defaultdict(dict)
        self._is_nulecule = is_nulecule or False

    def load(self, ask=False, skip_asking=False):
        """
        Load config data.
        """
        for param in self._params:
            value = self._answers[self._namespace].get(param[NAME_KEY]) or \
                self._answers[self._parent_ns].get(param[NAME_KEY]) or \
                self._answers[GLOBAL_CONF].get(param[NAME_KEY])
            if value is None and (ask or (
                    not skip_asking and param.get(DEFAULTNAME_KEY) is None)):
                cockpit_logger.info("%s is missing in answers.conf." % param[NAME_KEY])
                value = Utils.askfor(param[NAME_KEY], param)
            elif value is None:
                value = param.get(DEFAULTNAME_KEY)
            self._data[self._namespace][param[NAME_KEY]] = value

    def _split_namespace(self, namespace):
        """
        Split namespace to get parent and current namespace in a Nulecule.
        """
        if self._is_nulecule:
            return '', namespace
        words = namespace.rsplit('.', 1)
        parent, current = '', ''
        if len(words) == 2:
            parent, current = words[0], words[1]
        else:
            parent, current = '', words[0]
        return parent, current

    def context(self):
        """
        Get context to render artifact files in a Nulecule component.
        """
        context = {}

        context.update(copy.copy(self._data[GLOBAL_CONF]))
        context.update(copy.copy(self._data[self._namespace]))

        context.update(copy.copy(self._answers[GLOBAL_CONF]))
        context.update(copy.copy(self._answers[self._namespace]))

        return context
