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
   - ``GB4/Content/Text/en/Common/localized_text_skill_info.json``
   - ``GB4/Content/Text/en/Common/localized_text_skill_name.json``
   - ``GB4/Content/Text/en/Common/localized_text_ms_number.json``
   - ``GB4/Content/Text/en/Common/localized_text_parts_name.json``
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

3. Run ``poetry run generate "C:\FModel\Output\Exports\"``

