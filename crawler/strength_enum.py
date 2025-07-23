from enum import Enum

class StrengthEnum(Enum):
  VALUE = 1
  KIND = 2
  MOOD = 3
  PARKING = 4
  TASTE = 5


  @staticmethod
  def get_strength_by_id(id):
    mapping = {
      StrengthEnum.VALUE:"가성비",
      StrengthEnum.KIND:"친절",
      StrengthEnum.MOOD:"분위기",
      StrengthEnum.PARKING:"주차",
      StrengthEnum.TASTE:"맛",
    }
    return mapping.get(StrengthEnum(id),'')