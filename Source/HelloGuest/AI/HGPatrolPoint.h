#pragma once

#include "CoreMinimal.h"
#include "Engine/TargetPoint.h"
#include "HGPatrolPoint.generated.h"

/** A place the Guest walks to while patrolling. */
UCLASS()
class HELLOGUEST_API AHGPatrolPoint : public ATargetPoint
{
	GENERATED_BODY()

public:
	/** The point is used once the Guest phase reaches this value (0 = from the start). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Patrol")
	int32 MinPhase = 0;

	/** Relative chance to pick this point. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Patrol", meta = (ClampMin = "0"))
	float Weight = 1.f;

	/** Point inside a restricted room: the Guest occasionally peeks in. Keep its weight low. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Patrol")
	bool bInRestrictedRoom = false;
};
