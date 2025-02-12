# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from logging import Logger

from ax.modelbridge.transition_criterion import TransitionCriterion
from ax.utils.common.logger import get_logger

logger: Logger = get_logger(__name__)


class CompletionCriterion(TransitionCriterion):
    """
    Deprecated class that has been replaced by `TransitionCriterion`, and will be
    fully reaped in a future release.
    """

    logger.warning(
        "CompletionCriterion is deprecated, please use TransitionCriterion instead."
    )
    pass
