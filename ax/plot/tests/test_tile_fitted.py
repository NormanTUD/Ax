#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from unittest import mock

from ax.core import Experiment

from ax.core.arm import Arm
from ax.core.metric import Metric
from ax.core.search_space import SearchSpace
from ax.modelbridge.base import Adapter
from ax.models.discrete.full_factorial import FullFactorialGenerator
from ax.plot.scatter import tile_fitted, tile_observations
from ax.utils.common.testutils import TestCase
from ax.utils.testing.core_stubs import (
    get_data,
    get_experiment_with_data,
    get_search_space,
)
from ax.utils.testing.modeling_stubs import get_observation


@mock.patch(
    "ax.modelbridge.base.observations_from_data",
    autospec=True,
    return_value=([get_observation()]),
)
@mock.patch(
    "ax.modelbridge.base.gen_arms", autospec=True, return_value=[Arm(parameters={})]
)
def get_modelbridge(_, __, status_quo_name: str | None = None) -> Adapter:
    exp = Experiment(
        search_space=get_search_space(),
        status_quo=Arm(
            parameters={"w": 1.0, "x": 1.0, "y": "foo", "z": True}, name=status_quo_name
        )
        if status_quo_name is not None
        else None,
    )
    modelbridge = Adapter(
        experiment=exp, model=FullFactorialGenerator(), data=get_data()
    )
    modelbridge._predict = mock.MagicMock(
        "ax.modelbridge.base.Adapter._predict",
        autospec=True,
        return_value=[get_observation().data],
    )
    return modelbridge


class TileFittedTest(TestCase):
    def test_TileFitted(self) -> None:
        model = get_modelbridge(status_quo_name=None)

        # Should throw if `status_quo_arm` is None and rel=True
        with self.assertRaises(ValueError):
            tile_fitted(model, rel=True)
        tile_fitted(model, rel=False)

        model = get_modelbridge(status_quo_name="1_1")
        config = tile_fitted(model, rel=True)
        self.assertIsNotNone(config)

        for key in ["layout", "data"]:
            self.assertIn(key, config.data)

        # Layout
        for key in [
            "annotations",
            "margin",
            "hovermode",
            "updatemenus",
            "font",
            "width",
            "height",
            "legend",
        ]:
            self.assertIn(key, config.data["layout"])

        # Data
        for i in range(2):
            self.assertEqual(config.data["data"][i]["x"], ["1_1"])
            self.assertEqual(config.data["data"][i]["y"], [0.0])
            self.assertEqual(config.data["data"][i]["type"], "scatter")
            self.assertIn("Arm 1_1", config.data["data"][i]["text"][0])
            self.assertIn("[-138.593%, 138.593%]", config.data["data"][i]["text"][0])
            self.assertIn("0.0%", config.data["data"][i]["text"][0])

            for key in [
                "type",
                "x",
                "y",
                "marker",
                "mode",
                "name",
                "text",
                "hoverinfo",
                "error_y",
                "visible",
                "legendgroup",
                "showlegend",
                "xaxis",
                "yaxis",
            ]:
                self.assertIn(key, config.data["data"][i])


class TileObservationsTest(TestCase):
    def test_TileObservations(self) -> None:
        exp = get_experiment_with_data()
        exp.trials[0].run()
        exp.trials[0].mark_completed()
        exp.add_tracking_metric(Metric("ax_test_metric"))
        exp.search_space = SearchSpace(
            parameters=list(exp.search_space.parameters.values())
        )
        config = tile_observations(experiment=exp, arm_names=["0_0", "0_1"], rel=False)

        for key in ["layout", "data"]:
            self.assertIn(key, config.data)

        # Layout
        for key in [
            "annotations",
            "margin",
            "hovermode",
            "updatemenus",
            "font",
            "width",
            "height",
            "legend",
        ]:
            self.assertIn(key, config.data["layout"])

        self.assertEqual(
            config.data["layout"]["annotations"][0]["text"], "ax_test_metric"
        )

        # Data
        self.assertEqual(config.data["data"][0]["x"], ["0_0", "0_1"])
        self.assertEqual(config.data["data"][0]["y"], [3.0, 2.0])
        self.assertEqual(config.data["data"][0]["type"], "scatter")
        self.assertIn("Arm 0_0", config.data["data"][0]["text"][0])

        label_dict = {"ax_test_metric": "mapped_name"}
        config = tile_observations(
            experiment=exp, arm_names=["0_0", "0_1"], rel=False, label_dict=label_dict
        )
        self.assertEqual(config.data["layout"]["annotations"][0]["text"], "mapped_name")
