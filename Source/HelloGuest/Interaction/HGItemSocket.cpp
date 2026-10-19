#include "Interaction/HGItemSocket.h"
#include "Core/HGItemLibrary.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "UObject/ConstructorHelpers.h"

#define LOCTEXT_NAMESPACE "HGInteraction"

AHGItemSocket::AHGItemSocket()
{
	static ConstructorHelpers::FObjectFinder<UStaticMesh> SocketMesh(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> ItemMesh(TEXT("/Engine/BasicShapes/Sphere.Sphere"));

	if (SocketMesh.Succeeded())
	{
		Mesh->SetStaticMesh(SocketMesh.Object);
		Mesh->SetRelativeScale3D(FVector(0.15f, 0.15f, 0.1f));
	}

	InstalledMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("InstalledMesh"));
	InstalledMesh->SetupAttachment(Root);
	InstalledMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	if (ItemMesh.Succeeded())
	{
		InstalledMesh->SetStaticMesh(ItemMesh.Object);
		InstalledMesh->SetRelativeScale3D(FVector(0.15f));
		InstalledMesh->SetRelativeLocation(FVector(0.f, 0.f, 10.f));
	}

	bConsumeRequiredItem = true;
	InteractionText = LOCTEXT("Install", "Install");
}

bool AHGItemSocket::CanInteract_Implementation(AHGPlayerCharacter* Player) const
{
	return !bFilled && Super::CanInteract_Implementation(Player);
}

void AHGItemSocket::Interact_Implementation(AHGPlayerCharacter* Player)
{
	if (bFilled)
	{
		return;
	}

	bFilled = true;
	ApplyState();
	OnFilled(Player);
	Super::Interact_Implementation(Player);
}

FText AHGItemSocket::GetInteractionText_Implementation(AHGPlayerCharacter* Player) const
{
	if (bFilled)
	{
		return FText::GetEmpty();
	}
	return HasRequiredItem(Player)
		? FText::Format(LOCTEXT("InstallItem", "Install: {0}"), UHGItemLibrary::GetItemDisplayName(RequiredItem))
		: GetMissingItemText();
}

void AHGItemSocket::ApplyState()
{
	InstalledMesh->SetVisibility(bFilled);
}

#undef LOCTEXT_NAMESPACE
