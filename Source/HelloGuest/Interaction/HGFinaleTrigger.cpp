#include "Interaction/HGFinaleTrigger.h"
#include "AI/HGGuestCharacter.h"
#include "Components/BoxComponent.h"
#include "Components/SceneCaptureComponent2D.h"
#include "Core/HGWorldStateSubsystem.h"
#include "Animation/SkeletalMeshActor.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SceneCapture2D.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Controller.h"
#include "Internationalization/Culture.h"
#include "Internationalization/Internationalization.h"
#include "LevelSequenceActor.h"
#include "LevelSequencePlayer.h"
#include "Player/HGPlayerCharacter.h"
#include "Player/HGPlayerController.h"
#include "TimerManager.h"
#include "UI/HGHUD.h"

AHGFinaleTrigger::AHGFinaleTrigger()
{
	PrimaryActorTick.bCanEverTick = false;

	Volume = CreateDefaultSubobject<UBoxComponent>(TEXT("Volume"));
	Volume->SetBoxExtent(FVector(150.f));
	Volume->SetCollisionProfileName(TEXT("Trigger"));
	Volume->SetCanEverAffectNavigation(false);
	Volume->ShapeColor = FColor(200, 40, 40);
	SetRootComponent(Volume);
}

void AHGFinaleTrigger::BeginPlay()
{
	Super::BeginPlay();

	Volume->OnComponentBeginOverlap.AddDynamic(this, &AHGFinaleTrigger::HandleOverlap);
	if (RecordingCamera)
	{
		RecordingCamera->GetCaptureComponent2D()->bCaptureEveryFrame = false;
	}
}

void AHGFinaleTrigger::HandleOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp,
	int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (Cast<AHGPlayerCharacter>(OtherActor))
	{
		StartFinale();
	}
}

void AHGFinaleTrigger::StartFinale()
{
	if (bStarted || !Sequence)
	{
		return;
	}
	bStarted = true;

	APlayerController* PC = GetWorld()->GetFirstPlayerController();
	if (PC)
	{
		// The HUD stays on: it draws the subtitles.
		PC->SetCinematicMode(true, false, false, true, true);
		if (AHGPlayerCharacter* Player = Cast<AHGPlayerCharacter>(PC->GetPawn()))
		{
			Player->SetGodMode(true);
		}
	}
	SetGuestsFrozen(true);

	if (RecordingCamera)
	{
		RecordingCamera->GetCaptureComponent2D()->bCaptureEveryFrame = true;
	}
	for (int32 Index = 0; Index < Subtitles.Num(); ++Index)
	{
		FTimerHandle& Handle = LineTimers.AddDefaulted_GetRef();
		GetWorldTimerManager().SetTimer(Handle, FTimerDelegate::CreateUObject(this, &AHGFinaleTrigger::ShowLine, Index),
			FMath::Max(Subtitles[Index].Time, 0.01f), false);
	}
	if (ULevelSequencePlayer* Player = Sequence->GetSequencePlayer())
	{
		Player->OnFinished.AddUniqueDynamic(this, &AHGFinaleTrigger::HandleSequenceFinished);
		Player->Play();
	}
}

void AHGFinaleTrigger::ShowLine(int32 Index)
{
	if (!Subtitles.IsValidIndex(Index))
	{
		return;
	}
	const FHGSubtitleLine& Line = Subtitles[Index];
	const bool bRussian = FInternationalization::Get().GetCurrentLanguage()->GetTwoLetterISOLanguageName() == TEXT("ru");
	const FString& Body = bRussian && !Line.TextRU.IsEmpty() ? Line.TextRU : Line.TextEN;
	const FString Text = Line.Speaker.IsEmpty() ? Body : FString::Printf(TEXT("%s: %s"), *Line.Speaker, *Body);
	if (APlayerController* PC = GetWorld()->GetFirstPlayerController())
	{
		if (AHGHUD* HUD = Cast<AHGHUD>(PC->GetHUD()))
		{
			HUD->ShowSubtitle(FText::FromString(Text), Line.Duration);
		}
	}
}

void AHGFinaleTrigger::HandleSequenceFinished()
{
	if (RecordingCamera)
	{
		RecordingCamera->GetCaptureComponent2D()->bCaptureEveryFrame = false;
	}
	if (Speaker && SpeakerAnimAfter)
	{
		Speaker->AddActorWorldRotation(FRotator(0.f, SpeakerTurnAfter, 0.f));
		Speaker->GetSkeletalMeshComponent()->PlayAnimation(SpeakerAnimAfter, true);
	}
	if (APlayerController* PC = GetWorld()->GetFirstPlayerController())
	{
		PC->SetCinematicMode(false, false, false, true, true);
		PC->SetViewTargetWithBlend(PC->GetPawn(), 0.4f);
	}
	// The Guest stays frozen: the act is over.
	if (UHGWorldStateSubsystem* WorldState = UHGWorldStateSubsystem::Get(this))
	{
		WorldState->SetFlag(FlagOnFinish);
	}
}

void AHGFinaleTrigger::SetGuestsFrozen(bool bFrozen)
{
	for (TActorIterator<AHGGuestCharacter> It(GetWorld()); It; ++It)
	{
		It->SetActorHiddenInGame(bFrozen);
		It->SetActorEnableCollision(!bFrozen);
		It->SetActorTickEnabled(!bFrozen);
		if (AController* Controller = It->GetController())
		{
			Controller->SetActorTickEnabled(!bFrozen);
			Controller->StopMovement();
		}
	}
}
