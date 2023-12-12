import pytest
import os

from pycmo.configs.config import get_config
from pycmo.lib.actions import *
from pycmo.lib.tools import cmo_steam_observation_file_to_xml

config = get_config()

observation_file_path = os.path.join(config['pycmo_path'], 'tests', "fixtures", 'test_steam_observation.inst')
scenario_xml = cmo_steam_observation_file_to_xml(observation_file_path)

side = "Israel"
tanker_name = "Chevron #6"
aircraft_name = "Sufa #1"
aircraft_ID = "6352f8eb-db07-4916-8da7-33ef013878a0"
course_latitude = -90
course_longitude = 100
weapon_ID = 4369
weapon_qty = 4
mount_ID = 1256
target_name = "Bogey #1"
target_ID = "0HXVM6-0HMUTDCKTG4A6"

features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
action_space = AvailableFunctions(features=features)
unit_id = "05ba3413-d0cd-4a69-8513-2d7e55d28366"
unit_name = "Nahshon #1"
mount_id = 286
loadout_id = 3
mount_weapon_id = 1918
loadout_weapon_id = 516

launch_aircraft_test_parameters = [
    (side, aircraft_name, True, f"ScenEdit_SetUnit({{side = '{side}', name = '{aircraft_name}', Launch = true}})"),
    (side, aircraft_name, False, f"ScenEdit_SetUnit({{side = '{side}', name = '{aircraft_name}', Launch = false}})"),
]
manual_attack_contact_test_parameters = [
    (aircraft_ID, target_ID, weapon_ID, weapon_qty, mount_ID, f"ScenEdit_AttackContact('{aircraft_ID}', '{target_ID}' , {{mode='1', mount='{mount_ID}', weapon='{weapon_ID}', qty='{weapon_qty}'}})"),
    (aircraft_ID, target_ID, weapon_ID, weapon_qty, None, f"ScenEdit_AttackContact('{aircraft_ID}', '{target_ID}' , {{mode='1', weapon='{weapon_ID}', qty='{weapon_qty}'}})"),
]
rtb_test_parameters = [
    (side, aircraft_name, True, f"ScenEdit_SetUnit({{side = '{side}', name = '{aircraft_name}', RTB = true}})"),
    (side, aircraft_name, False, f"ScenEdit_SetUnit({{side = '{side}', name = '{aircraft_name}', RTB = false}})"),
]
contains_test_parameters = [
    (0, [], True),
    (0, [1], False),
    (1, [side, aircraft_name, True], True),
    (1, [side, aircraft_name], False),
    (1, [side, aircraft_ID, True], False),
    (2, [side, aircraft_ID, course_latitude, course_longitude], False),
    (2, [side, aircraft_name, course_latitude, course_longitude], True),
    (2, [side, aircraft_name, 200, 200], False),
]

def test_no_op():
    assert no_op() == ""

@pytest.mark.parametrize("side, aircraft_name, launch, expected", launch_aircraft_test_parameters)
def test_launch_aircraft(side, aircraft_name, launch, expected):
    assert launch_aircraft(side, aircraft_name, launch) == expected

def test_set_unit_course():
    assert set_unit_course(side, aircraft_ID, course_latitude, course_longitude) == f"ScenEdit_SetUnit({{side = '{side}', name = '{aircraft_ID}', course = {{{{longitude = {course_longitude}, latitude = {course_latitude}, TypeOf = 'ManualPlottedCourseWaypoint'}}}}}})"

@pytest.mark.parametrize("attacker_id, contact_id, weapon_id, qty, mount_id, expected", manual_attack_contact_test_parameters)
def test_manual_attack_contact(attacker_id, contact_id, weapon_id, qty, mount_id, expected):
    assert manual_attack_contact(attacker_id, contact_id, weapon_id, qty, mount_id) == expected

def test_auto_attack_contact():
    assert auto_attack_contact(aircraft_ID, target_ID) == f"ScenEdit_AttackContact('{aircraft_ID}', '{target_ID}', {{mode='0'}})"

def test_refuel_unit():
    assert refuel_unit(side, aircraft_name, tanker_name) == f"ScenEdit_RefuelUnit({{side='{side}', unitname='{aircraft_name}', tanker='{tanker_name}'}})"

def test_auto_refuel_unit():
    assert auto_refuel_unit(side, aircraft_name) == f"ScenEdit_RefuelUnit({{side='{side}', unitname='{aircraft_name}'}})"

@pytest.mark.parametrize("side, aircraft_name, return_to_base, expected", rtb_test_parameters)
def test_rtb(side, aircraft_name, return_to_base, expected):
    assert rtb(side, aircraft_name, return_to_base) == expected

def test_action_space():
    assert isinstance(action_space, AvailableFunctions)

def test_action_space_sides():
    assert len(action_space.sides) == 1
    assert action_space.sides[0] == side

def test_action_space_unit_ids():
    assert len(action_space.unit_ids) == 9
    assert isinstance(action_space.unit_ids[0], str)
    assert action_space.unit_ids[0] == "8e2750c4-6c86-46a4-8dfa-16507c7f71e3"

def test_action_space_unit_names():
    assert len(action_space.unit_names) == 9
    assert isinstance(action_space.unit_names[0], str)
    assert action_space.unit_names[1] == unit_name

def test_action_space_contact_ids():
    assert len(action_space.contact_ids) == 8
    assert isinstance(action_space.contact_ids[0], str)
    assert action_space.contact_ids[0] == "0HXVM6-0HMUTDCKTG4AA"

def test_action_space_mount_ids():
    assert len(action_space.mount_ids) == 12
    assert action_space.mount_ids[0] == mount_id

def test_action_space_loadout_ids():
    assert len(action_space.loadout_ids) == 8
    assert action_space.loadout_ids[0] == loadout_id

def test_action_space_weapon_ids():
    assert len(action_space.weapon_ids) == 45
    assert action_space.weapon_ids[0] == mount_weapon_id

def test_action_space_weapon_qtys():
    assert len(action_space.weapon_qtys) == 45
    assert action_space.weapon_qtys[0] == 5

def test_action_space_valid_function_args():
    function_args = action_space.get_valid_function_args()
    assert isinstance(function_args, dict)
    launch_aircraft_args = function_args['launch_aircraft']
    assert isinstance(launch_aircraft_args, list)
    assert aircraft_name in launch_aircraft_args[1]

def test_action_space_valid_functions():
    manual_attack_fnc = action_space.VALID_FUNCTIONS[3]
    assert isinstance(action_space.VALID_FUNCTIONS, list)
    assert len(action_space.VALID_FUNCTIONS) == 8
    assert isinstance(manual_attack_fnc, Function)
    assert manual_attack_fnc.id == 3
    assert manual_attack_fnc.name == "manual_attack_contact"
    assert manual_attack_fnc.corresponding_def == manual_attack_contact
    assert isinstance(manual_attack_fnc.args, list)
    weapon_id_args = manual_attack_fnc.args[2]
    assert isinstance(weapon_id_args, list)
    assert isinstance(list(weapon_id_args)[0], int)
    weapon_qty_args = manual_attack_fnc.args[3]
    assert isinstance(weapon_qty_args, list)
    assert isinstance(list(weapon_qty_args)[0], int)
    mount_id_args = manual_attack_fnc.args[4]
    assert isinstance(mount_id_args, list)
    assert isinstance(list(mount_id_args)[0], int)

def test_action_space_sample():
    action = action_space.sample()
    assert isinstance(action, str)
    # assert action == ""

@pytest.mark.parametrize("function_id, function_args, expected", contains_test_parameters)
def test_action_space_contains(function_id, function_args, expected):
    assert action_space.contains(function_id=function_id, function_args=function_args) == expected
