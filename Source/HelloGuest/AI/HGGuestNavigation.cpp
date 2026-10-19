#include "AI/HGGuestNavigation.h"

UHGNavArea_GuestRestricted::UHGNavArea_GuestRestricted()
{
	DefaultCost = 1.f;
	DrawColor = FColor(255, 140, 0);
}

UHGNavFilter_GuestPatrol::UHGNavFilter_GuestPatrol()
{
	FNavigationFilterArea Restricted;
	Restricted.AreaClass = UHGNavArea_GuestRestricted::StaticClass();
	Restricted.bIsExcluded = true;
	Areas.Add(Restricted);
}
