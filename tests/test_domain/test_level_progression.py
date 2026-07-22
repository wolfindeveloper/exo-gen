from app.domain.services.level_progression import (
    LevelProgressionService,
    ZONE_UNLOCK_TABLE,
    SLOT_UNLOCK_TABLE,
)


class TestCalculateLevel:
    def test_zero_xp_is_level_1(self):
        assert LevelProgressionService.calculate_level(0) == 1

    def test_negative_xp_is_level_1(self):
        assert LevelProgressionService.calculate_level(-100) == 1

    def test_level_boundaries(self):
        assert LevelProgressionService.calculate_level(999) == 1
        assert LevelProgressionService.calculate_level(1000) == 2
        assert LevelProgressionService.calculate_level(1999) == 2
        assert LevelProgressionService.calculate_level(2000) == 3
        assert LevelProgressionService.calculate_level(25000) == 26


class TestCalculateExpeditionXp:
    def test_one_hour_5_percent_risk(self):
        # 20*1 + 5*2 = 30
        assert LevelProgressionService.calculate_expedition_xp(3600, 0.05) == 30

    def test_half_hour_low_risk(self):
        # 20*0.5 + 1*2 = 12
        assert LevelProgressionService.calculate_expedition_xp(1800, 0.01) == 12

    def test_minimum_guaranteed(self):
        # Даже 1 минута с 0% риска даёт минимум 5 XP
        assert LevelProgressionService.calculate_expedition_xp(60, 0.0) == 5

    def test_long_high_risk_expedition(self):
        # 8 часов + 40% = 160 + 80 = 240
        assert LevelProgressionService.calculate_expedition_xp(8 * 3600, 0.40) == 240


class TestMaxArtifactSlots:
    def test_level_1_gives_4_slots(self):
        assert LevelProgressionService.get_max_artifact_slots(1) == 4

    def test_level_4_still_4_slots(self):
        assert LevelProgressionService.get_max_artifact_slots(4) == 4

    def test_level_5_gives_6_slots(self):
        assert LevelProgressionService.get_max_artifact_slots(5) == 6

    def test_level_14_still_6_slots(self):
        assert LevelProgressionService.get_max_artifact_slots(14) == 6

    def test_level_15_gives_8_slots(self):
        assert LevelProgressionService.get_max_artifact_slots(15) == 8

    def test_level_100_gives_8_slots(self):
        assert LevelProgressionService.get_max_artifact_slots(100) == 8


class TestCanAccessZone:
    def test_level_1_can_access_t1(self):
        status = LevelProgressionService.can_access_zone(1, 1)
        assert status.is_unlocked is True

    def test_level_1_cannot_access_t2(self):
        status = LevelProgressionService.can_access_zone(1, 2)
        assert status.is_unlocked is False
        assert status.required_level == 3

    def test_level_3_can_access_t2(self):
        status = LevelProgressionService.can_access_zone(3, 2)
        assert status.is_unlocked is True

    def test_level_10_cannot_access_t4(self):
        status = LevelProgressionService.can_access_zone(10, 4)
        assert status.is_unlocked is False
        assert status.required_level == 12

    def test_all_unlock_tables_cover_all_tiers(self):
        """Все 5 тиров должны быть в таблице."""
        assert set(ZONE_UNLOCK_TABLE.keys()) == {1, 2, 3, 4, 5}


class TestNextUnlocks:
    def test_next_slot_unlock_for_new_player(self):
        result = LevelProgressionService.get_next_slot_unlock(1)
        assert result == (5, 6)

    def test_next_slot_unlock_after_6_slots(self):
        result = LevelProgressionService.get_next_slot_unlock(6)
        assert result == (15, 8)

    def test_next_slot_unlock_when_all_open(self):
        result = LevelProgressionService.get_next_slot_unlock(20)
        assert result is None

    def test_next_zone_unlock_for_new_player(self):
        result = LevelProgressionService.get_next_zone_unlock(1)
        assert result == (3, 2)  # Следующая — T2 на 3 уровне

    def test_next_zone_unlock_when_all_open(self):
        result = LevelProgressionService.get_next_zone_unlock(30)
        assert result is None
