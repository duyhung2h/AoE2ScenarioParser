from unittest import TestCase

from AoE2ScenarioParser.helper.pretty_format import pretty_format_dict

from AoE2ScenarioParser.objects.support.enums.group_by import GroupBy

from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.objects.managers.de.trigger_manager_de import TriggerManagerDE
from AoE2ScenarioParser.scenarios.aoe2_scenario import initialise_version_dependencies

initialise_version_dependencies("DE", 1.43)


class Test(TestCase):
    tm: TriggerManagerDE

    def setUp(self) -> None:
        self.tm = TriggerManagerDE([], [], [])

    def test_copy_trigger_tree_per_player_attributes(self):
        trigger = self.tm.add_trigger("Trigger0")
        trigger.new_effect.create_object(object_list_unit_id=1, source_player=PlayerId.ONE)
        trigger.new_effect.create_object(source_player=PlayerId.TWO)

        self.tm.copy_trigger_tree_per_player(from_player=PlayerId.ONE, trigger_select=0)

        self.assertListEqual(
            [t.name for t in self.tm.triggers],
            ["Trigger0 (p1)", "Trigger0 (p2)", "Trigger0 (p3)", "Trigger0 (p4)",
             "Trigger0 (p5)", "Trigger0 (p6)", "Trigger0 (p7)", "Trigger0 (p8)", ]
        )

        for index, player in enumerate(PlayerId.all(exclude_gaia=True)):
            self.assertEqual(self.tm.triggers[index].effects[0].object_list_unit_id, 1)
            self.assertEqual(self.tm.triggers[index].effects[0].source_player, player)

            if index != 0:  # First entry is source trigger. Remains unchanged
                self.assertEqual(self.tm.triggers[index].effects[1].source_player, player)

    def test_copy_trigger_tree_per_player_groupby_none(self):
        self.tm.add_trigger("Trigger0").new_effect.activate_trigger(trigger_id=1)
        self.tm.add_trigger("Trigger1")

        new_triggers = self.tm.copy_trigger_tree_per_player(from_player=PlayerId.ONE, trigger_select=0)

        self.assertListEqual(
            [t.name for t in self.tm.triggers],
            [
                "Trigger0 (p1)",
                "Trigger1 (p1)",
                "Trigger0 (p2)", "Trigger0 (p3)", "Trigger0 (p4)", "Trigger0 (p5)", "Trigger0 (p6)", "Trigger0 (p7)",
                "Trigger0 (p8)",
                "Trigger1 (p2)", "Trigger1 (p3)", "Trigger1 (p4)", "Trigger1 (p5)", "Trigger1 (p6)", "Trigger1 (p7)",
                "Trigger1 (p8)"
            ]
        )

        # Verify if triggers still link to their new copy
        for player, triggers in new_triggers.items():
            self.assertEqual(triggers[0].effects[0].trigger_id, triggers[1].trigger_id)

    def test_copy_trigger_tree_per_player_groupby_trigger(self):
        self.tm.add_trigger("Trigger0")
        self.tm.add_trigger("Trigger1").new_effect.activate_trigger(trigger_id=2)
        self.tm.add_trigger("Trigger2")
        self.tm.add_trigger("Trigger3")

        new_triggers = self.tm.copy_trigger_tree_per_player(
            from_player=PlayerId.ONE, trigger_select=1, group_triggers_by=GroupBy.TRIGGER
        )

        self.assertListEqual(
            [t.name for t in self.tm.triggers],
            [
                "Trigger0",
                "Trigger1 (p1)", "Trigger1 (p2)", "Trigger1 (p3)", "Trigger1 (p4)",
                "Trigger1 (p5)", "Trigger1 (p6)", "Trigger1 (p7)", "Trigger1 (p8)",
                "Trigger2 (p1)", "Trigger2 (p2)", "Trigger2 (p3)", "Trigger2 (p4)",
                "Trigger2 (p5)", "Trigger2 (p6)", "Trigger2 (p7)", "Trigger2 (p8)",
                "Trigger3",
            ]
        )

        # Verify if triggers still link to their new copy
        for player, triggers in new_triggers.items():
            self.assertEqual(triggers[0].effects[0].trigger_id, triggers[1].trigger_id)

    def test_copy_trigger_tree_per_player_groupby_trigger_extended(self):
        self.tm.add_trigger("Trigger0")
        self.tm.add_trigger("Trigger1").new_effect.activate_trigger(trigger_id=2)
        self.tm.add_trigger("Trigger2").new_effect.activate_trigger(trigger_id=0)
        self.tm.add_trigger("Trigger3")

        new_triggers = self.tm.copy_trigger_tree_per_player(
            from_player=PlayerId.ONE, trigger_select=1, group_triggers_by=GroupBy.TRIGGER
        )

        self.assertListEqual(
            [t.name for t in self.tm.triggers],
            [
                "Trigger1 (p1)", "Trigger1 (p2)", "Trigger1 (p3)", "Trigger1 (p4)",
                "Trigger1 (p5)", "Trigger1 (p6)", "Trigger1 (p7)", "Trigger1 (p8)",
                "Trigger2 (p1)", "Trigger2 (p2)", "Trigger2 (p3)", "Trigger2 (p4)",
                "Trigger2 (p5)", "Trigger2 (p6)", "Trigger2 (p7)", "Trigger2 (p8)",
                "Trigger0 (p1)", "Trigger0 (p2)", "Trigger0 (p3)", "Trigger0 (p4)",
                "Trigger0 (p5)", "Trigger0 (p6)", "Trigger0 (p7)", "Trigger0 (p8)",
                "Trigger3",
            ]
        )

        # Verify if triggers still link to their new copy
        for player, triggers in new_triggers.items():
            self.assertEqual(triggers[0].effects[0].trigger_id, triggers[1].trigger_id)
            self.assertEqual(triggers[1].effects[0].trigger_id, triggers[2].trigger_id)

    def test_copy_trigger_tree_per_player_groupby_player(self):
        self.tm.add_trigger("Trigger0")
        self.tm.add_trigger("Trigger1").new_effect.activate_trigger(trigger_id=2)
        self.tm.add_trigger("Trigger2")
        self.tm.add_trigger("Trigger3")

        new_triggers = self.tm.copy_trigger_tree_per_player(
            from_player=PlayerId.ONE, trigger_select=1, group_triggers_by=GroupBy.PLAYER
        )

        self.assertListEqual(
            [t.name for t in self.tm.triggers],
            [
                "Trigger0",
                "Trigger1 (p1)", "Trigger2 (p1)",
                "Trigger1 (p2)", "Trigger2 (p2)",
                "Trigger1 (p3)", "Trigger2 (p3)",
                "Trigger1 (p4)", "Trigger2 (p4)",
                "Trigger1 (p5)", "Trigger2 (p5)",
                "Trigger1 (p6)", "Trigger2 (p6)",
                "Trigger1 (p7)", "Trigger2 (p7)",
                "Trigger1 (p8)", "Trigger2 (p8)",
                "Trigger3",
            ]
        )

        # Verify if triggers still link to their new copy
        for player, triggers in new_triggers.items():
            self.assertEqual(triggers[0].effects[0].trigger_id, triggers[1].trigger_id)

    def test_copy_trigger_tree_per_player_groupby_player_extended(self):
        self.tm.add_trigger("Trigger0")
        self.tm.add_trigger("Trigger1").new_effect.activate_trigger(trigger_id=2)
        self.tm.add_trigger("Trigger2").new_effect.activate_trigger(trigger_id=0)
        self.tm.add_trigger("Trigger3")

        new_triggers = self.tm.copy_trigger_tree_per_player(
            from_player=PlayerId.ONE, trigger_select=1, group_triggers_by=GroupBy.PLAYER
        )

        self.assertListEqual(
            [t.name for t in self.tm.triggers],
            [
                "Trigger1 (p1)", "Trigger2 (p1)", "Trigger0 (p1)",
                "Trigger1 (p2)", "Trigger2 (p2)", "Trigger0 (p2)",
                "Trigger1 (p3)", "Trigger2 (p3)", "Trigger0 (p3)",
                "Trigger1 (p4)", "Trigger2 (p4)", "Trigger0 (p4)",
                "Trigger1 (p5)", "Trigger2 (p5)", "Trigger0 (p5)",
                "Trigger1 (p6)", "Trigger2 (p6)", "Trigger0 (p6)",
                "Trigger1 (p7)", "Trigger2 (p7)", "Trigger0 (p7)",
                "Trigger1 (p8)", "Trigger2 (p8)", "Trigger0 (p8)",
                "Trigger3"
            ]
        )

        # Verify if triggers still link to their new copy
        for player, triggers in new_triggers.items():
            self.assertEqual(triggers[0].effects[0].trigger_id, triggers[1].trigger_id)
            self.assertEqual(triggers[1].effects[0].trigger_id, triggers[2].trigger_id)
