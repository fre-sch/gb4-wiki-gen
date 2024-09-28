# GB4 WIKI GEN

Generate content pages for https://gundambreaker.miraheze.org

## Requirements

- Python
- Poetry

## Install

1. Run ``poetry install``.

2. Extract JSON data from GB4 into a directory, eg ``C:\FModel\Output``. These
files are required to generate content:

   - ``GB4/Content/Text/en/Common/localized_text_ability_cartridge_name.json``
   - ``GB4/Content/Text/en/Common/localized_text_ability_cartridge_info.json``
   - ``GB4/Content/Text/en/Common/localized_text_preset_character_name.json``
   - ``GB4/Content/Text/en/Common/localized_text_ms_number.json``
   - ``GB4/Content/Text/en/Common/localized_text_skill_info.json``
   - ``GB4/Content/Text/en/Common/localized_text_skill_name.json``
   - ``GB4/Content/Text/en/Common/localized_text_parts_name.json``
   - ``GB4/Content/Text/en/Common/localized_text_weapon_name.json``
   - ``GB4/Content/Text/en/Common/localized_text_shield_name.json``
   - ``GB4/Content/Text/en/Common/localized_text_bparts_name.json``
   - ``GB4/Content/Text/en/Common/localized_text_gundam_series.json``
   - ``GB4/Content/Text/en/Menu/localized_text_story_title_name.json``
   - ``GB4/Content/Data/MS/AbilityCartridge.json``
   - ``GB4/Content/Data/MS/AbilityInfo.json``
   - ``GB4/Content/Data/MS/AbilityPerformance.json``
   - ``GB4/Content/Data/MS/EquipAttachParameter.json``
   - ``GB4/Content/Data/MS/EquipParameter.json``
   - ``GB4/Content/Data/MS/EquipPerformance.json``
   - ``GB4/Content/Data/MS/MSList.json``
   - ``GB4/Content/Data/MS/PartsIdList.json``
   - ``GB4/Content/Data/MS/PartsParameter.json``
   - ``GB4/Content/Data/Item/ItemGunplaBox.json``
   - ``GB4/Content/Data/Skill/SkillIdInfo.json``
   - ``GB4/Content/Data/Item/ItemDrop/MissionRewardTable.json``
   - ``GB4/Content/Data/Mission/MissionListTable.json``
   - ``GB4/Content/Data/Synthesize/DerivedSynthesizeParameter.json``
   - ``GB4/Content/Data/UI/Menu/ShopGoodsTable.json``

3. Create file ``config.toml`` with content:
  ```toml
  [wiki_client]
  username = "<your gundambreaker.miraheze.com bot account>"
  password = "<your gundambreaker.miraheze.com bot password>"
  ```

4. Run ``poetry run generate`` to see all commands the generator provides