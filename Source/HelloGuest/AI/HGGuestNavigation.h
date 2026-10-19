#pragma once

#include "CoreMinimal.h"
#include "NavAreas/NavArea.h"
#include "NavFilters/NavigationQueryFilter.h"
#include "HGGuestNavigation.generated.h"

/**
 * Rooms the Guest does not enter on his own (the two rooms by the entrance).
 * Mark them with a NavModifierVolume using this area class.
 */
UCLASS()
class HELLOGUEST_API UHGNavArea_GuestRestricted : public UNavArea
{
	GENERATED_BODY()

public:
	UHGNavArea_GuestRestricted();
};

/** Used for patrolling and investigating: restricted rooms are excluded. Chasing uses the default filter. */
UCLASS()
class HELLOGUEST_API UHGNavFilter_GuestPatrol : public UNavigationQueryFilter
{
	GENERATED_BODY()

public:
	UHGNavFilter_GuestPatrol();
};
