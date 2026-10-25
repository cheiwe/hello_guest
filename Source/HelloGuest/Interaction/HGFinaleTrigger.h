#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "HGFinaleTrigger.generated.h"

class UBoxComponent;
class ALevelSequenceActor;
class ASceneCapture2D;
class ASkeletalMeshActor;
class UAnimationAsset;

/** One subtitle of a cutscene, in both languages of the game. */
USTRUCT(BlueprintType)
struct FHGSubtitleLine
{
	GENERATED_BODY()

	/** Seconds from the start of the cutscene. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Subtitle")
	float Time = 0.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Subtitle")
	float Duration = 3.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Subtitle")
	FString Speaker;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Subtitle")
	FString TextEN;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Subtitle")
	FString TextRU;
};

/**
 * End of Act 1 (Vitec_Play): when the player walks into the box, the cutscene sequence plays with the
 * player locked and safe from the Guest, the subtitles appear on time, and the CCTV camera over the van
 * feeds the monitor while the recording is shown. Fires once; sets FlagOnFinish at the end.
 */
UCLASS()
class HELLOGUEST_API AHGFinaleTrigger : public AActor
{
	GENERATED_BODY()

public:
	AHGFinaleTrigger();

	/** Starts the cutscene (also the console command HGFinale). */
	UFUNCTION(BlueprintCallable, Category = "Hello Guest|Finale")
	void StartFinale();

	UPROPERTY(EditAnywhere, Category = "Finale")
	TObjectPtr<ALevelSequenceActor> Sequence;

	/** Renders the "recording" into the monitor's render target while the cutscene runs. */
	UPROPERTY(EditAnywhere, Category = "Finale")
	TObjectPtr<ASceneCapture2D> RecordingCamera;

	UPROPERTY(EditAnywhere, Category = "Finale")
	TArray<FHGSubtitleLine> Subtitles;

	UPROPERTY(EditAnywhere, Category = "Finale")
	FName FlagOnFinish = TEXT("Act1.Finished");

	/** Character of the cutscene (Vitec) and the looping animation he keeps once it is over. */
	UPROPERTY(EditAnywhere, Category = "Finale")
	TObjectPtr<ASkeletalMeshActor> Speaker;

	UPROPERTY(EditAnywhere, Category = "Finale")
	TObjectPtr<UAnimationAsset> SpeakerAnimAfter;

	/** Yaw added to the speaker when that animation starts (it may be authored facing the other way). */
	UPROPERTY(EditAnywhere, Category = "Finale")
	float SpeakerTurnAfter = 0.f;

protected:
	virtual void BeginPlay() override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UBoxComponent> Volume;

private:
	UFUNCTION()
	void HandleOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp,
		int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

	UFUNCTION()
	void HandleSequenceFinished();

	void ShowLine(int32 Index);
	void SetGuestsFrozen(bool bFrozen);

	bool bStarted = false;
	TArray<FTimerHandle> LineTimers;
};
