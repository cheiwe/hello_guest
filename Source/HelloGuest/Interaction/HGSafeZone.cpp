#include "Interaction/HGSafeZone.h"
#include "Components/BoxComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"

AHGSafeZone::AHGSafeZone()
{
	PrimaryActorTick.bCanEverTick = false;

	Volume = CreateDefaultSubobject<UBoxComponent>(TEXT("Volume"));
	Volume->SetBoxExtent(FVector(150.f));
	Volume->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Volume->SetCanEverAffectNavigation(false);
	Volume->ShapeColor = FColor(40, 160, 60);
	SetRootComponent(Volume);
}

bool AHGSafeZone::IsLocationSafe(const UObject* WorldContext, const FVector& Location)
{
	const UWorld* World = WorldContext ? WorldContext->GetWorld() : nullptr;
	if (!World)
	{
		return false;
	}

	for (TActorIterator<AHGSafeZone> It(World); It; ++It)
	{
		const FTransform& Transform = It->Volume->GetComponentTransform();
		const FVector Local = Transform.InverseTransformPosition(Location);
		const FVector Extent = It->Volume->GetUnscaledBoxExtent();
		if (FMath::Abs(Local.X) <= Extent.X && FMath::Abs(Local.Y) <= Extent.Y && FMath::Abs(Local.Z) <= Extent.Z)
		{
			return true;
		}
	}
	return false;
}
