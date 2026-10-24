#include "AI/HGGuestAIController.h"
#include "AI/HGGuestCharacter.h"
#include "AI/HGGuestNavigation.h"
#include "AI/HGPatrolPoint.h"
#include "Player/HGPlayerCharacter.h"
#include "Core/HGGameMode.h"
#include "Core/HGGameplaySettings.h"
#include "Core/HGWorldStateSubsystem.h"
#include "Interaction/HGSafeZone.h"
#include "Components/CapsuleComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "HelloGuest.h"
#include "EngineUtils.h"
#include "Navigation/PathFollowingComponent.h"
#include "NavigationSystem.h"
#include "Perception/AIPerceptionComponent.h"
#include "Perception/AISenseConfig_Hearing.h"
#include "Perception/AISenseConfig_Sight.h"
#include "Perception/AISense_Hearing.h"
#include "Perception/AISense_Sight.h"

AHGGuestAIController::AHGGuestAIController()
{
	PrimaryActorTick.bCanEverTick = true;

	const UHGGameplaySettings* Settings = UHGGameplaySettings::Get();

	UAIPerceptionComponent* Perception = CreateDefaultSubobject<UAIPerceptionComponent>(TEXT("Perception"));
	SetPerceptionComponent(*Perception);

	SightConfig = CreateDefaultSubobject<UAISenseConfig_Sight>(TEXT("SightConfig"));
	SightConfig->SightRadius = Settings->SightRadius;
	SightConfig->LoseSightRadius = Settings->LoseSightRadius;
	SightConfig->PeripheralVisionAngleDegrees = Settings->PeripheralVisionHalfAngle;
	SightConfig->SetMaxAge(5.f);
	SightConfig->DetectionByAffiliation.bDetectEnemies = true;
	SightConfig->DetectionByAffiliation.bDetectNeutrals = true;
	SightConfig->DetectionByAffiliation.bDetectFriendlies = true;

	HearingConfig = CreateDefaultSubobject<UAISenseConfig_Hearing>(TEXT("HearingConfig"));
	HearingConfig->HearingRange = Settings->HearingRange;
	HearingConfig->SetMaxAge(3.f);
	HearingConfig->DetectionByAffiliation.bDetectEnemies = true;
	HearingConfig->DetectionByAffiliation.bDetectNeutrals = true;
	HearingConfig->DetectionByAffiliation.bDetectFriendlies = true;

	Perception->ConfigureSense(*SightConfig);
	Perception->ConfigureSense(*HearingConfig);
	Perception->SetDominantSense(SightConfig->GetSenseImplementation());
}

void AHGGuestAIController::BeginPlay()
{
	Super::BeginPlay();
	GetPerceptionComponent()->OnTargetPerceptionUpdated.AddDynamic(this, &AHGGuestAIController::HandlePerception);
}

void AHGGuestAIController::OnPossess(APawn* InPawn)
{
	Super::OnPossess(InPawn);
	ResetToPatrol();
}

AHGGuestCharacter* AHGGuestAIController::GetGuest() const
{
	return Cast<AHGGuestCharacter>(GetPawn());
}

// --- Senses --------------------------------------------------------------------

bool AHGGuestAIController::CanNoticePlayer(const AHGPlayerCharacter* Player) const
{
	if (!Player || Player->IsDead() || !GetPawn())
	{
		return false;
	}

	if (AHGSafeZone::IsLocationSafe(this, Player->GetActorLocation()))
	{
		return false;
	}

	const float Distance = FVector::Dist(Player->GetActorLocation(), GetPawn()->GetActorLocation());
	return !Player->IsConcealed() || Distance <= UHGGameplaySettings::Get()->DarkZoneDetectDistance;
}

bool AHGGuestAIController::CanSeePlayerUpClose(const AHGPlayerCharacter* Player) const
{
	if (!CanNoticePlayer(Player))
	{
		return false;
	}

	const APawn* Guest = GetPawn();
	const FVector ToPlayer = Player->GetActorLocation() - Guest->GetActorLocation();
	if (ToPlayer.Size() > UHGGameplaySettings::Get()->CloseSightDistance)
	{
		return false;
	}

	// In front and to the sides, not behind his back: sneaking past him from behind still works.
	const FVector Facing = Guest->GetActorForwardVector().GetSafeNormal2D();
	if (FVector::DotProduct(Facing, ToPlayer.GetSafeNormal2D()) < -0.35f)
	{
		return false;
	}
	return HasClearViewTo(Player);
}

bool AHGGuestAIController::HasClearViewTo(const AHGPlayerCharacter* Player) const
{
	const FVector Eyes = GetPawn()->GetPawnViewLocation();
	const FVector Body = Player->GetActorLocation();
	const FVector Head = Body + FVector(0.f, 0.f, Player->GetCapsuleComponent()->GetScaledCapsuleHalfHeight() * 0.6f);

	FCollisionQueryParams Params(SCENE_QUERY_STAT(HGGuestView), false, GetPawn());
	Params.AddIgnoredActor(Player);
	return !GetWorld()->LineTraceTestByChannel(Eyes, Body, ECC_Visibility, Params)
		|| !GetWorld()->LineTraceTestByChannel(Eyes, Head, ECC_Visibility, Params);
}

AHGPlayerCharacter* AHGGuestAIController::GetLocalPlayerCharacter() const
{
	const APlayerController* PC = GetWorld()->GetFirstPlayerController();
	return PC ? Cast<AHGPlayerCharacter>(PC->GetPawn()) : nullptr;
}

void AHGGuestAIController::HandlePerception(AActor* Actor, FAIStimulus Stimulus)
{
	AHGPlayerCharacter* Player = Cast<AHGPlayerCharacter>(Actor);

	if (Stimulus.Type == UAISense::GetSenseID<UAISense_Sight>())
	{
		if (!Player)
		{
			return;
		}

		if (Stimulus.WasSuccessfullySensed())
		{
			PlayerInSight = Player;
		}
		else
		{
			if (PlayerInSight == Player)
			{
				PlayerInSight.Reset();
			}
			if (State == EHGGuestState::Chase)
			{
				LastKnownLocation = Stimulus.StimulusLocation;
			}
		}
		// Tick decides whether the player is actually noticed (dark zones).
		return;
	}

	if (Stimulus.Type == UAISense::GetSenseID<UAISense_Hearing>())
	{
		if (State == EHGGuestState::Chase || State == EHGGuestState::Incapacitated || State == EHGGuestState::GiveUp || bCaught
			|| !Stimulus.WasSuccessfullySensed() || AHGSafeZone::IsLocationSafe(this, Stimulus.StimulusLocation))
		{
			return;
		}

		Alert = FMath::Min(100.f, Alert + UHGGameplaySettings::Get()->HearingAlertGain * Stimulus.Strength);
		LastKnownLocation = Stimulus.StimulusLocation;
		EnterState(EHGGuestState::Investigate);
	}
}

// --- State machine -------------------------------------------------------------

void AHGGuestAIController::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	if (!GetPawn() || State == EHGGuestState::Incapacitated || bCaught)
	{
		return;
	}

	const UHGGameplaySettings* Settings = UHGGameplaySettings::Get();
	StateTime += DeltaSeconds;

	if (State != EHGGuestState::Chase)
	{
		AHGPlayerCharacter* Seen = PlayerInSight.Get();
		AHGPlayerCharacter* Nearby = GetLocalPlayerCharacter();
		if (Seen && CanNoticePlayer(Seen) && LineOfSightTo(Seen))
		{
			StartChase(Seen);
		}
		else if (Nearby && CanSeePlayerUpClose(Nearby))
		{
			StartChase(Nearby);
		}
	}

	if (State == EHGGuestState::Chase)
	{
		TickChase(DeltaSeconds);
		return;
	}

	Alert = FMath::Max(0.f, Alert - Settings->AlertDecayPerSecond * DeltaSeconds);

	if (State == EHGGuestState::Search && (StateTime >= Settings->SearchDuration || Alert < Settings->CalmAlert))
	{
		EnterState(EHGGuestState::Patrol);
		return;
	}

	if (WaitRemaining > 0.f)
	{
		WaitRemaining -= DeltaSeconds;
		if (WaitRemaining <= 0.f)
		{
			if (State == EHGGuestState::Patrol)
			{
				MoveToNextPatrolPoint();
			}
			else if (State == EHGGuestState::Search)
			{
				MoveToSearchPoint();
			}
			else if (State == EHGGuestState::GiveUp)
			{
				// Done fuming: back to the house and the yard.
				EnterState(EHGGuestState::Patrol);
			}
		}
	}
}

void AHGGuestAIController::TickChase(float DeltaSeconds)
{
	AHGPlayerCharacter* Player = Target.Get();
	if (!Player || Player->IsDead())
	{
		return;
	}

	const UHGGameplaySettings* Settings = UHGGameplaySettings::Get();

	if (AHGSafeZone::IsLocationSafe(this, Player->GetActorLocation()))
	{
		GiveUp();
		return;
	}

	// Re-path a few times per second if the previous move ended (reached a partial path end, etc.).
	RepathCooldown -= DeltaSeconds;
	if (RepathCooldown <= 0.f && GetMoveStatus() == EPathFollowingStatus::Idle)
	{
		RepathCooldown = 0.25f;
		MoveToActor(Player, Settings->CatchDistance * 0.5f, true, true, false, TSubclassOf<UNavigationQueryFilter>(), true);
	}

	if ((CanNoticePlayer(Player) && LineOfSightTo(Player)) || CanSeePlayerUpClose(Player))
	{
		TimeSinceSeen = 0.f;
		LastKnownLocation = Player->GetActorLocation();

		if (FVector::Dist(Player->GetActorLocation(), GetPawn()->GetActorLocation()) <= Settings->CatchDistance && !Player->IsGodMode())
		{
			CatchPlayer();
		}
		return;
	}

	TimeSinceSeen += DeltaSeconds;
	if (TimeSinceSeen >= Settings->LoseTargetTime)
	{
		Alert = 100.f;
		EnterState(EHGGuestState::Search);
	}
}

void AHGGuestAIController::StartChase(AHGPlayerCharacter* Player)
{
	const bool bWasChasing = State == EHGGuestState::Chase;

	Target = Player;
	Alert = 100.f;
	TimeSinceSeen = 0.f;
	bAllowRestricted = true;
	LastKnownLocation = Player->GetActorLocation();
	EnterState(EHGGuestState::Chase);

	MoveToActor(Player, UHGGameplaySettings::Get()->CatchDistance * 0.5f, true, true, false, TSubclassOf<UNavigationQueryFilter>(), true);

	if (!bWasChasing)
	{
		if (AHGGuestCharacter* Guest = GetGuest())
		{
			Guest->OnChaseStarted();
		}
	}
}

void AHGGuestAIController::CatchPlayer()
{
	AHGPlayerCharacter* Player = Target.Get();
	AHGGuestCharacter* Guest = GetGuest();
	if (!Player || !Guest)
	{
		return;
	}

	bCaught = true;
	StopMovement();
	Guest->PlayCatchAnimation();
	Guest->OnCaughtPlayer();

	if (AHGGameMode* GameMode = GetWorld()->GetAuthGameMode<AHGGameMode>())
	{
		GameMode->HandlePlayerCaught(Guest, Player);
	}
}

void AHGGuestAIController::GiveUp()
{
	const AHGPlayerCharacter* Player = Target.Get();
	const UHGGameplaySettings* Settings = UHGGameplaySettings::Get();

	StopMovement();
	Alert = 50.f;
	EnterState(EHGGuestState::GiveUp);

	float Duration = Settings->GiveUpDuration;
	if (AHGGuestCharacter* Guest = GetGuest())
	{
		const float AnimLength = Guest->PlayGiveUpAnimation(Player ? Player->GetActorLocation() : LastKnownLocation);
		if (AnimLength > 0.f)
		{
			Duration = AnimLength;
		}
	}
	WaitRemaining = Duration;
}

void AHGGuestAIController::EnterState(EHGGuestState NewState)
{
	State = NewState;
	StateTime = 0.f;
	WaitRemaining = 0.f;

	const TSubclassOf<UNavigationQueryFilter> Filter = bAllowRestricted
		? TSubclassOf<UNavigationQueryFilter>()
		: TSubclassOf<UNavigationQueryFilter>(UHGNavFilter_GuestPatrol::StaticClass());

	switch (NewState)
	{
	case EHGGuestState::Patrol:
		Target.Reset();
		bAllowRestricted = false;
		WaitRemaining = 0.5f;
		break;

	case EHGGuestState::Investigate:
	case EHGGuestState::Search:
		RequestMove(LastKnownLocation, 80.f, Filter, true);
		break;

	case EHGGuestState::GiveUp:
		Target.Reset();
		bAllowRestricted = false;
		break;

	default:
		break;
	}

	UpdateSpeed();
}

void AHGGuestAIController::OnMoveCompleted(FAIRequestID RequestID, const FPathFollowingResult& Result)
{
	Super::OnMoveCompleted(RequestID, Result);

	// A new move replaced the old one; the new state already handles it.
	if (Result.IsInterrupted())
	{
		return;
	}
	HandleMoveFinished();
}

void AHGGuestAIController::HandleMoveFinished()
{
	const UHGGameplaySettings* Settings = UHGGameplaySettings::Get();
	switch (State)
	{
	case EHGGuestState::Patrol:
		WaitRemaining = FMath::FRandRange(Settings->PatrolWaitMin, Settings->PatrolWaitMax);
		break;

	case EHGGuestState::Investigate:
		// Reached the noise: look around the area.
		State = EHGGuestState::Search;
		StateTime = 0.f;
		WaitRemaining = 1.5f;
		UpdateSpeed();
		break;

	case EHGGuestState::Search:
		WaitRemaining = FMath::FRandRange(1.f, 2.5f);
		break;

	case EHGGuestState::Chase:
		// Never start a new move from here: a move that completes instantly (partial path, target
		// off the navmesh) would call back into this function and recurse. TickChase re-paths.
		break;

	default:
		break;
	}
}

void AHGGuestAIController::MoveToNextPatrolPoint()
{
	const UHGWorldStateSubsystem* WorldState = UHGWorldStateSubsystem::Get(this);
	const int32 Phase = WorldState ? WorldState->GetGuestPhase() : 0;
	const FVector PawnLocation = GetPawn()->GetActorLocation();

	TArray<AHGPatrolPoint*> Candidates;
	float TotalWeight = 0.f;
	for (TActorIterator<AHGPatrolPoint> It(GetWorld()); It; ++It)
	{
		if (It->MinPhase <= Phase && It->Weight > 0.f && FVector::Dist(It->GetActorLocation(), PawnLocation) > 150.f)
		{
			Candidates.Add(*It);
			TotalWeight += It->Weight;
		}
	}

	if (Candidates.IsEmpty())
	{
		// No patrol points placed: wander around.
		if (const UNavigationSystemV1* Nav = UNavigationSystemV1::GetNavigationSystem(GetWorld()))
		{
			FNavLocation Point;
			if (Nav->GetRandomReachablePointInRadius(PawnLocation, 1500.f, Point))
			{
				RequestMove(Point.Location, 50.f, UHGNavFilter_GuestPatrol::StaticClass(), false);
				return;
			}
		}
		WaitRemaining = 2.f;
		return;
	}

	float Roll = FMath::FRandRange(0.f, TotalWeight);
	AHGPatrolPoint* Chosen = Candidates.Last();
	for (AHGPatrolPoint* Point : Candidates)
	{
		Roll -= Point->Weight;
		if (Roll <= 0.f)
		{
			Chosen = Point;
			break;
		}
	}

	const TSubclassOf<UNavigationQueryFilter> Filter = Chosen->bInRestrictedRoom
		? TSubclassOf<UNavigationQueryFilter>()
		: TSubclassOf<UNavigationQueryFilter>(UHGNavFilter_GuestPatrol::StaticClass());
	// No partial paths: a point behind boards would leave him loitering at the nearest reachable spot.
	RequestMove(Chosen->GetActorLocation(), 50.f, Filter, true, false);
}

void AHGGuestAIController::MoveToSearchPoint()
{
	const UNavigationSystemV1* Nav = UNavigationSystemV1::GetNavigationSystem(GetWorld());
	FNavLocation Point;
	if (!Nav || !Nav->GetRandomReachablePointInRadius(LastKnownLocation, UHGGameplaySettings::Get()->SearchRadius, Point)
		|| AHGSafeZone::IsLocationSafe(this, Point.Location))
	{
		WaitRemaining = 1.f;
		return;
	}

	const TSubclassOf<UNavigationQueryFilter> Filter = bAllowRestricted
		? TSubclassOf<UNavigationQueryFilter>()
		: TSubclassOf<UNavigationQueryFilter>(UHGNavFilter_GuestPatrol::StaticClass());
	RequestMove(Point.Location, 60.f, Filter, false);
}

void AHGGuestAIController::UpdateSpeed()
{
	AHGGuestCharacter* Guest = GetGuest();
	if (!Guest)
	{
		return;
	}

	const UHGGameplaySettings* Settings = UHGGameplaySettings::Get();
	float Speed = Settings->PatrolSpeed;
	if (State == EHGGuestState::Chase)
	{
		Speed = Settings->ChaseSpeed;
	}
	else if (State == EHGGuestState::Investigate || State == EHGGuestState::Search)
	{
		Speed = Settings->PatrolSpeed * 1.3f;
	}

	const UHGWorldStateSubsystem* WorldState = UHGWorldStateSubsystem::Get(this);
	Guest->SetBaseSpeed(Speed * (WorldState ? WorldState->GetGuestSpeedMultiplier() : 1.f));
}

void AHGGuestAIController::SetIncapacitated(bool bValue)
{
	if (bValue)
	{
		if (State != EHGGuestState::Incapacitated)
		{
			StateBeforeIncapacitated = State;
		}
		StopMovement();
		State = EHGGuestState::Incapacitated;
		return;
	}

	if (State != EHGGuestState::Incapacitated)
	{
		return;
	}

	// Recover: after a chase or search keep looking where the player was last seen.
	EnterState(StateBeforeIncapacitated == EHGGuestState::Patrol ? EHGGuestState::Patrol : EHGGuestState::Search);
}

void AHGGuestAIController::ResetToPatrol()
{
	StopMovement();
	Alert = 0.f;
	Target.Reset();
	PlayerInSight.Reset();
	bCaught = false;
	bAllowRestricted = false;
	EnterState(EHGGuestState::Patrol);
}

void AHGGuestAIController::RequestMove(const FVector& Destination, float AcceptanceRadius, TSubclassOf<UNavigationQueryFilter> Filter,
	bool bProjectToNavigation, bool bAllowPartialPath)
{
	const EPathFollowingRequestResult::Type Result =
		MoveToLocation(Destination, AcceptanceRadius, true, true, bProjectToNavigation, false, Filter, bAllowPartialPath);
	if (Result == EPathFollowingRequestResult::AlreadyAtGoal)
	{
		// No move starts, so OnMoveCompleted never fires: without this he would stand in Investigate forever.
		HandleMoveFinished();
		return;
	}
	if (Result != EPathFollowingRequestResult::Failed)
	{
		return;
	}

	// A failed request never reaches OnMoveCompleted: schedule a retry, otherwise the Guest freezes.
	if (State == EHGGuestState::Investigate)
	{
		State = EHGGuestState::Search;
		StateTime = 0.f;
	}
	WaitRemaining = 1.f;

	const UNavigationSystemV1* Nav = UNavigationSystemV1::GetNavigationSystem(GetWorld());
	if (!bWarnedNoNavMesh && (!Nav || !Nav->GetDefaultNavDataInstance()))
	{
		bWarnedNoNavMesh = true;
		UE_LOG(LogHelloGuest, Warning, TEXT("Guest cannot move: the level has no navigation mesh (NavMeshBoundsVolume)."));
		if (GEngine)
		{
			GEngine->AddOnScreenDebugMessage(-1, 10.f, FColor::Red, TEXT("Hello Guest: no navmesh on this level - the Guest cannot move"));
		}
	}
}
