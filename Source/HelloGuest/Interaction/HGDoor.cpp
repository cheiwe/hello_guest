#include "Interaction/HGDoor.h"
#include "Interaction/HGObstacle.h"
#include "Player/HGPlayerCharacter.h"
#include "Player/HGInventoryComponent.h"
#include "AI/HGGuestCharacter.h"
#include "Core/HGItemLibrary.h"
#include "Core/HGTypes.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "UObject/ConstructorHelpers.h"

#define LOCTEXT_NAMESPACE "HGInteraction"

AHGDoor::AHGDoor()
{
	PrimaryActorTick.bCanEverTick = true;

	Hinge = CreateDefaultSubobject<USceneComponent>(TEXT("Hinge"));
	Hinge->SetupAttachment(Root);
	Mesh->SetupAttachment(Hinge);

	static ConstructorHelpers::FObjectFinder<UStaticMesh> Placeholder(TEXT("/Engine/BasicShapes/Cube.Cube"));
	if (Placeholder.Succeeded())
	{
		// 10 x 100 x 210 cm panel whose left edge sits on the hinge.
		Mesh->SetStaticMesh(Placeholder.Object);
		Mesh->SetRelativeScale3D(FVector(0.1f, 1.f, 2.1f));
		Mesh->SetRelativeLocation(FVector(0.f, 50.f, 105.f));
	}
	Mesh->SetCanEverAffectNavigation(false);

	GuestDetector = CreateDefaultSubobject<UBoxComponent>(TEXT("GuestDetector"));
	GuestDetector->SetupAttachment(Root);
	GuestDetector->SetBoxExtent(FVector(150.f, 80.f, 100.f));
	GuestDetector->SetRelativeLocation(FVector(0.f, 50.f, 100.f));
	GuestDetector->SetCollisionProfileName(TEXT("OverlapAllDynamic"));
	GuestDetector->SetCollisionResponseToChannel(ECC_Visibility, ECR_Ignore);
	GuestDetector->SetCanEverAffectNavigation(false);
}

bool AHGDoor::IsFullyUnlocked() const
{
	return Locks.FindByPredicate([](const FHGDoorLock& Lock) { return !Lock.bUnlocked; }) == nullptr;
}

bool AHGDoor::IsLockReady(const FHGDoorLock& Lock) const
{
	if (Lock.bUnlocked || (Lock.BlockedBy && !Lock.BlockedBy->IsCleared()))
	{
		return false;
	}

	for (const FName& Required : Lock.RequiresLocks)
	{
		const FHGDoorLock* Other = Locks.FindByPredicate([Required](const FHGDoorLock& L) { return L.LockId == Required; });
		if (Other && !Other->bUnlocked)
		{
			return false;
		}
	}
	return true;
}

int32 AHGDoor::FindOpenableLock(const AHGPlayerCharacter* Player) const
{
	for (int32 Index = 0; Index < Locks.Num(); ++Index)
	{
		if (IsLockReady(Locks[Index]) && Player && Player->GetInventory()->HasItem(Locks[Index].KeyItem))
		{
			return Index;
		}
	}
	return INDEX_NONE;
}

bool AHGDoor::CanInteract_Implementation(AHGPlayerCharacter* Player) const
{
	return IsFullyUnlocked() || FindOpenableLock(Player) != INDEX_NONE;
}

void AHGDoor::Interact_Implementation(AHGPlayerCharacter* Player)
{
	if (IsFullyUnlocked())
	{
		SetOpen(!bOpen);
		EmitNoise(0.2f, 500.f);
		return;
	}

	const int32 Index = FindOpenableLock(Player);
	if (Index == INDEX_NONE)
	{
		return;
	}

	FHGDoorLock& Lock = Locks[Index];
	Lock.bUnlocked = true;
	EmitNoise(0.3f, 700.f);
	OnLockOpened(Lock.LockId);
	SetWorldFlag(HGFlags::Lock(Lock.LockId));

	if (IsFullyUnlocked())
	{
		Super::Interact_Implementation(Player);
	}
}

FText AHGDoor::GetInteractionText_Implementation(AHGPlayerCharacter* Player) const
{
	if (IsFullyUnlocked())
	{
		return bOpen ? LOCTEXT("Close", "Close") : LOCTEXT("Open", "Open");
	}

	const int32 Index = FindOpenableLock(Player);
	if (Index != INDEX_NONE)
	{
		return FText::Format(LOCTEXT("Unlock", "Unlock: {0}"), UHGItemLibrary::GetItemDisplayName(Locks[Index].KeyItem));
	}

	const bool bBlocked = Locks.ContainsByPredicate([](const FHGDoorLock& Lock)
	{
		return !Lock.bUnlocked && Lock.BlockedBy && !Lock.BlockedBy->IsCleared();
	});
	return bBlocked ? LOCTEXT("Blocked", "Something covers the lock") : LOCTEXT("Locked", "Locked");
}

void AHGDoor::SetOpen(bool bInOpen)
{
	if (bInOpen && !IsFullyUnlocked())
	{
		return;
	}
	bOpen = bInOpen;
}

void AHGDoor::BeginPlay()
{
	Super::BeginPlay();
	GuestDetector->OnComponentBeginOverlap.AddDynamic(this, &AHGDoor::HandleGuestOverlap);
}

void AHGDoor::ApplyState()
{
	CurrentAngle = bOpen ? OpenAngle : 0.f;
	Hinge->SetRelativeRotation(FRotator(0.f, CurrentAngle, 0.f));
}

void AHGDoor::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	const float Target = bOpen ? OpenAngle : 0.f;
	if (!FMath::IsNearlyEqual(CurrentAngle, Target))
	{
		CurrentAngle = FMath::FInterpConstantTo(CurrentAngle, Target, DeltaSeconds, SwingSpeed);
		Hinge->SetRelativeRotation(FRotator(0.f, CurrentAngle, 0.f));
	}
}

void AHGDoor::HandleGuestOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp,
	int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (!bOpen && IsFullyUnlocked() && Cast<AHGGuestCharacter>(OtherActor))
	{
		SetOpen(true);
	}
}

#undef LOCTEXT_NAMESPACE
