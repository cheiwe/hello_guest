#include "Interaction/HGObstacle.h"
#include "Core/HGTypes.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "UObject/ConstructorHelpers.h"

#define LOCTEXT_NAMESPACE "HGInteraction"

AHGObstacle::AHGObstacle()
{
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Placeholder(TEXT("/Engine/BasicShapes/Cube.Cube"));
	if (Placeholder.Succeeded())
	{
		Mesh->SetStaticMesh(Placeholder.Object);
		Mesh->SetRelativeScale3D(FVector(0.1f, 1.f, 2.f));
		Mesh->SetRelativeLocation(FVector(0.f, 0.f, 100.f));
	}

	RequiredItem = HGItems::Crowbar;
	InteractionText = LOCTEXT("Break", "Break");
}

bool AHGObstacle::CanInteract_Implementation(AHGPlayerCharacter* Player) const
{
	return !bCleared && Super::CanInteract_Implementation(Player);
}

void AHGObstacle::Interact_Implementation(AHGPlayerCharacter* Player)
{
	if (bCleared)
	{
		return;
	}

	bCleared = true;
	ApplyState();
	EmitNoise(NoiseLoudness, NoiseRange);
	OnCleared(Player);
	Super::Interact_Implementation(Player);
}

void AHGObstacle::ApplyState()
{
	SetActorHiddenInGame(bCleared);
	SetActorEnableCollision(!bCleared);
}

#undef LOCTEXT_NAMESPACE
