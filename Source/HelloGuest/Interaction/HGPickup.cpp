#include "Interaction/HGPickup.h"
#include "Player/HGPlayerCharacter.h"
#include "Player/HGInventoryComponent.h"
#include "Core/HGItemLibrary.h"
#include "Core/HGTypes.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "UObject/ConstructorHelpers.h"

#define LOCTEXT_NAMESPACE "HGInteraction"

AHGPickup::AHGPickup()
{
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Placeholder(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	if (Placeholder.Succeeded())
	{
		Mesh->SetStaticMesh(Placeholder.Object);
		Mesh->SetRelativeScale3D(FVector(0.2f));
	}
	Mesh->SetCollisionProfileName(TEXT("OverlapAllDynamic"));
	Mesh->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
}

void AHGPickup::Interact_Implementation(AHGPlayerCharacter* Player)
{
	if (bCollected || !Player->GetInventory()->AddItem(ItemId, Count))
	{
		return;
	}

	bCollected = true;
	ApplyState();
	SetWorldFlag(HGFlags::Item(ItemId));
	Super::Interact_Implementation(Player);
}

FText AHGPickup::GetInteractionText_Implementation(AHGPlayerCharacter* Player) const
{
	return FText::Format(LOCTEXT("Take", "Take: {0}"), UHGItemLibrary::GetItemDisplayName(ItemId));
}

void AHGPickup::ApplyState()
{
	SetActorHiddenInGame(bCollected);
	SetActorEnableCollision(!bCollected);
}

#undef LOCTEXT_NAMESPACE
