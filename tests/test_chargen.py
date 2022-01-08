from pathlib import Path
from hyperborea.chargen import (
    DB,
    ac_to_aac,
    calculate_ac,
    get_alignment,
    get_attr,
    get_attr_mod,
    get_class_level_data,
    get_class_list,
    get_gender,
    get_hd,
    get_level,
    get_qualifying_classes,
    get_race_id,
    get_save_bonuses,
    get_starting_armour,
    get_starting_shield,
    get_thief_skills,
    roll_hit_points,
    roll_stats,
)
from valid_data import (
    VALID_ABILITY_SCORES,
    VALID_ABILITIES,
    VALID_CA,
    VALID_CLASS_IDS,
    VALID_DICE_METHODS,
    VALID_FA,
    VALID_GENDERS,
    VALID_HD_PLUS,
    VALID_HD_QTY,
    VALID_HD_SIZE,
    VALID_LEVELS,
    VALID_RACE_IDS,
    VALID_SAVES,
    VALID_TA,
)


def test_db():
    assert Path(DB).is_file()


def test_roll_stats():
    for class_id in VALID_CLASS_IDS:
        for i in range(100):
            attr = roll_stats(method=6, class_id=class_id)
            for stat in attr.keys():
                assert stat in VALID_ABILITIES
                assert attr[stat]["score"] in VALID_ABILITY_SCORES
    for method in VALID_DICE_METHODS[:5]:
        for i in range(1000):
            attr = roll_stats(method=method)
            for stat in attr.keys():
                assert stat in VALID_ABILITIES
                assert attr[stat]["score"] in VALID_ABILITY_SCORES


def test_get_class_list():
    class_list = get_class_list(subclasses=True)
    assert len(class_list) == 33
    class_list = get_class_list(subclasses=False)
    assert len(class_list) == 4


def test_get_qualifying_classes():
    subclasses = True
    for i in range(1000):
        attr = get_attr()
        qual_classes = get_qualifying_classes(attr, subclasses)
        for c in qual_classes:
            assert c in VALID_CLASS_IDS
    subclasses = False
    for i in range(1000):
        attr = get_attr()
        qual_classes = get_qualifying_classes(attr, subclasses)
        for c in qual_classes:
            assert c in range(1, 5)


def test_get_level():
    for class_id in VALID_CLASS_IDS:
        for xp in range(0, 1000000, 1000):
            level = get_level(class_id, xp)
            assert level in VALID_LEVELS


def test_get_race_id():
    for i in range(1000):
        race_id = get_race_id()
        assert race_id in VALID_RACE_IDS


def test_get_gender():
    for i in range(1000):
        gender = get_gender()
        assert gender in VALID_GENDERS


def test_get_save_bonuses():
    for class_id in VALID_CLASS_IDS:
        sv_bonus = get_save_bonuses(class_id)
        for k, v in sv_bonus.items():
            assert v in [0, 2]
        # barbarians, berserkers, and paladins get +2 to all saves
        if class_id in [5, 6, 9, 27]:
            assert sum([v for v in sv_bonus.values()]) == 10
        # all others get +2 to two saves
        else:
            assert sum([v for v in sv_bonus.values()]) == 4


def test_get_class_level_data():
    for class_id in VALID_CLASS_IDS:
        for level in VALID_LEVELS:
            cl_data = get_class_level_data(class_id, level)
            assert cl_data["fa"] in VALID_FA
            assert cl_data["ca"] in VALID_CA
            assert cl_data["ta"] in VALID_TA
            assert cl_data["sv"] in VALID_SAVES


def test_get_hd():
    for class_id in VALID_CLASS_IDS:
        for level in VALID_LEVELS:
            hd = get_hd(class_id, level)
            qty = hd.split("d")[0]
            # number of dice in 1-9
            assert int(qty) in VALID_HD_QTY
            part2 = hd.split("d")[1].split("+")
            assert len(part2) in [1, 2]
            # die size in d4, d6, d8, d10, d12
            assert int(part2[0]) in VALID_HD_SIZE
            if len(part2) == 2:
                # +hp in 1,2,3; 2,4,6; 3,6,9; 4,8,12
                assert int(part2[1]) in VALID_HD_PLUS


def test_roll_hit_points():
    max_possible_hp = (10 * 12) + (12 * 3)  # Barbarian
    for class_id in range(1, 34):
        for level in range(1, 13):
            for cn_score in range(3, 19):
                mods = get_attr_mod("cn", cn_score)
                hp_adj = mods["hp_adj"]
                hp = roll_hit_points(class_id, level, hp_adj)
                assert level <= hp <= max_possible_hp


def test_starting_armour():
    for class_id in range(1, 34):
        armour = get_starting_armour(class_id)
        assert list(armour.keys()) == [
            "armour_id",
            "armour_type",
            "ac",
            "dr",
            "weight_class",
            "mv",
            "cost",
            "weight",
            "description",
        ]


def test_starting_shield():
    for class_id in range(1, 34):
        shield = get_starting_shield(class_id)
        assert shield is None or list(shield.keys()) == [
            "shield_id",
            "shield_type",
            "def_mod",
            "cost",
            "weight",
        ]


def test_calculate_ac():
    for class_id in range(1, 34):
        armour = get_starting_armour(class_id)
        shield = get_starting_shield(class_id)
        shield_def_mod = shield["def_mod"] if shield is not None else 0
        for dx_score in range(3, 19):
            dx_mod = get_attr_mod("dx", dx_score)
            ac = calculate_ac(
                armour["ac"],
                shield_def_mod,
                dx_mod["def_adj"],
            )
            # all AC values for starting characters should be 1 to 11 (level 1)
            # This may need updating after we include higher-level PCs,
            #   depending on if they have any abilities that improve AC
            assert ac in range(
                1, 12
            ), f"""invalid ac:
                class_id       = {class_id}
                armour_ac      = {armour["ac"]}
                shield_def_mod = {shield_def_mod}
                dx_score       = {dx_score}
                dx_def_adj     = {dx_mod["def_adj"]}
                ac             = {ac}
            """


def test_ac_to_aac():
    for ac in range(-10, 20):
        aac = ac_to_aac(ac)
        assert ac + aac == 19


def test_alignment():
    for class_id in VALID_CLASS_IDS:
        alignment = get_alignment(class_id)
        if class_id in [1, 2, 3, 7, 8, 11, 13, 18, 19]:
            allowed_alignments = ["CE", "CG", "LE", "LG", "N"]
        elif class_id in [4, 24, 25, 26, 31]:
            allowed_alignments = ["CE", "CG", "LE", "N"]
        elif class_id == 10:
            allowed_alignments = ["CG", "LG", "N"]
        elif class_id in [14, 22, 30]:
            allowed_alignments = ["CE", "LE", "N"]
        elif class_id in [15, 16, 21, 23, 29, 32]:
            allowed_alignments = ["CE", "CG", "N"]
        elif class_id in [12, 28]:
            allowed_alignments = ["LE", "LG", "N"]
        elif class_id in [5, 6, 20]:
            allowed_alignments = ["CE", "CG"]
        elif class_id == 33:
            allowed_alignments = ["LE", "N"]
        elif class_id == 9:
            allowed_alignments = ["LG"]
        elif class_id == 27:
            allowed_alignments = ["LE"]
        elif class_id == 17:
            allowed_alignments = ["N"]
        else:
            raise ValueError(f"Unexpected class_id: {class_id}")

        assert (
            alignment["short_name"] in allowed_alignments
        ), f"""
            Unexpected alignment '{alignment}' not in
            allowed values {allowed_alignments}
        """


def test_get_thief_skills():
    # classes without thief skills
    for class_id in [
        1,
        2,
        3,
        7,
        9,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        19,
        20,
        21,
        27,
        28,
        29,
        30,
    ]:
        thief_skills = get_thief_skills(class_id, 1, 10, 10, 10)
        assert (
            thief_skills is None
        ), f"class_id: {class_id} is not supposed to have thief skills"

    # level 1 thief with 10's
    expected_thief_skills = [
        {"thief_skill": "climb", "skill_name": "Climb", "skill_roll": 8, "stat": "dx"},
        {
            "thief_skill": "decipher_script",
            "skill_name": "Decipher Script",
            "skill_roll": 0,
            "stat": "in",
        },
        {
            "thief_skill": "discern_noise",
            "skill_name": "Discern Noise",
            "skill_roll": 4,
            "stat": "ws",
        },
        {"thief_skill": "hide", "skill_name": "Hide", "skill_roll": 5, "stat": "dx"},
        {
            "thief_skill": "manipulate_traps",
            "skill_name": "Manipulate Traps",
            "skill_roll": 3,
            "stat": "dx",
        },
        {
            "thief_skill": "move_silently",
            "skill_name": "Move Silently",
            "skill_roll": 5,
            "stat": "dx",
        },
        {
            "thief_skill": "open_locks",
            "skill_name": "Open Locks",
            "skill_roll": 3,
            "stat": "dx",
        },
        {
            "thief_skill": "pick_pockets",
            "skill_name": "Pick Pockets",
            "skill_roll": 4,
            "stat": "dx",
        },
        {
            "thief_skill": "read_scrolls",
            "skill_name": "Read Scrolls",
            "skill_roll": None,
            "stat": "in",
        },
    ]
    thief_skills = get_thief_skills(4, 1, 10, 10, 10)
    assert thief_skills == expected_thief_skills

    # level 1 thief with 16's
    expected_thief_skills = [
        {"thief_skill": "climb", "skill_name": "Climb", "skill_roll": 9, "stat": "dx"},
        {
            "thief_skill": "decipher_script",
            "skill_name": "Decipher Script",
            "skill_roll": 1,
            "stat": "in",
        },
        {
            "thief_skill": "discern_noise",
            "skill_name": "Discern Noise",
            "skill_roll": 5,
            "stat": "ws",
        },
        {"thief_skill": "hide", "skill_name": "Hide", "skill_roll": 6, "stat": "dx"},
        {
            "thief_skill": "manipulate_traps",
            "skill_name": "Manipulate Traps",
            "skill_roll": 4,
            "stat": "dx",
        },
        {
            "thief_skill": "move_silently",
            "skill_name": "Move Silently",
            "skill_roll": 6,
            "stat": "dx",
        },
        {
            "thief_skill": "open_locks",
            "skill_name": "Open Locks",
            "skill_roll": 4,
            "stat": "dx",
        },
        {
            "thief_skill": "pick_pockets",
            "skill_name": "Pick Pockets",
            "skill_roll": 5,
            "stat": "dx",
        },
        {
            "thief_skill": "read_scrolls",
            "skill_name": "Read Scrolls",
            "skill_roll": None,
            "stat": "in",
        },
    ]
    thief_skills = get_thief_skills(4, 1, 16, 16, 16)
    assert thief_skills == expected_thief_skills

    # level 12 thief with 10's
    expected_thief_skills = [
        {"thief_skill": "climb", "skill_name": "Climb", "skill_roll": 10, "stat": "dx"},
        {
            "thief_skill": "decipher_script",
            "skill_name": "Decipher Script",
            "skill_roll": 5,
            "stat": "in",
        },
        {
            "thief_skill": "discern_noise",
            "skill_name": "Discern Noise",
            "skill_roll": 9,
            "stat": "ws",
        },
        {"thief_skill": "hide", "skill_name": "Hide", "skill_roll": 10, "stat": "dx"},
        {
            "thief_skill": "manipulate_traps",
            "skill_name": "Manipulate Traps",
            "skill_roll": 8,
            "stat": "dx",
        },
        {
            "thief_skill": "move_silently",
            "skill_name": "Move Silently",
            "skill_roll": 10,
            "stat": "dx",
        },
        {
            "thief_skill": "open_locks",
            "skill_name": "Open Locks",
            "skill_roll": 8,
            "stat": "dx",
        },
        {
            "thief_skill": "pick_pockets",
            "skill_name": "Pick Pockets",
            "skill_roll": 9,
            "stat": "dx",
        },
        {
            "thief_skill": "read_scrolls",
            "skill_name": "Read Scrolls",
            "skill_roll": 5,
            "stat": "in",
        },
    ]
    thief_skills = get_thief_skills(4, 12, 10, 10, 10)
    assert thief_skills == expected_thief_skills

    # level 12 thief with 16's
    expected_thief_skills = [
        {"thief_skill": "climb", "skill_name": "Climb", "skill_roll": 11, "stat": "dx"},
        {
            "thief_skill": "decipher_script",
            "skill_name": "Decipher Script",
            "skill_roll": 6,
            "stat": "in",
        },
        {
            "thief_skill": "discern_noise",
            "skill_name": "Discern Noise",
            "skill_roll": 10,
            "stat": "ws",
        },
        {"thief_skill": "hide", "skill_name": "Hide", "skill_roll": 11, "stat": "dx"},
        {
            "thief_skill": "manipulate_traps",
            "skill_name": "Manipulate Traps",
            "skill_roll": 9,
            "stat": "dx",
        },
        {
            "thief_skill": "move_silently",
            "skill_name": "Move Silently",
            "skill_roll": 11,
            "stat": "dx",
        },
        {
            "thief_skill": "open_locks",
            "skill_name": "Open Locks",
            "skill_roll": 9,
            "stat": "dx",
        },
        {
            "thief_skill": "pick_pockets",
            "skill_name": "Pick Pockets",
            "skill_roll": 10,
            "stat": "dx",
        },
        {
            "thief_skill": "read_scrolls",
            "skill_name": "Read Scrolls",
            "skill_roll": 6,
            "stat": "in",
        },
    ]
    thief_skills = get_thief_skills(4, 12, 16, 16, 16)
    assert thief_skills == expected_thief_skills
