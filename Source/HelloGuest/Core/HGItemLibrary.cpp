#include "Core/HGItemLibrary.h"
#include "Core/HGTypes.h"

#define LOCTEXT_NAMESPACE "HGItems"

FText UHGItemLibrary::GetItemDisplayName(FName ItemId)
{
	if (ItemId == HGItems::Crowbar)     return LOCTEXT("Crowbar", "Crowbar");
	if (ItemId == HGItems::Scissors)    return LOCTEXT("Scissors", "Scissors");
	if (ItemId == HGItems::UpstairsKey) return LOCTEXT("UpstairsKey", "Small key");
	if (ItemId == HGItems::KeyRed)      return LOCTEXT("KeyRed", "Red key");
	if (ItemId == HGItems::KeyBlue)     return LOCTEXT("KeyBlue", "Blue key");
	if (ItemId == HGItems::KeyYellow)   return LOCTEXT("KeyYellow", "Yellow key");
	if (ItemId == HGItems::KeyGreen)    return LOCTEXT("KeyGreen", "Green key");
	if (ItemId == HGItems::Fuse)        return LOCTEXT("Fuse", "Fuse");
	if (ItemId == HGItems::Bulb)        return LOCTEXT("Bulb", "Light bulb");
	if (ItemId == HGItems::Antenna)     return LOCTEXT("Antenna", "Satellite dish");
	if (ItemId == HGItems::SpaceGun)    return LOCTEXT("SpaceGun", "Space gun");
	return FText::FromName(ItemId);
}

#undef LOCTEXT_NAMESPACE
