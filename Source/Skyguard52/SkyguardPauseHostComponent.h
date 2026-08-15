#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "SkyguardPauseHostComponent.generated.h"

class UInputComponent;
class USkyguardPauseSettingsWidget;

/** PlayerController-owned pause input and settings widget host. */
UCLASS(ClassGroup=(Skyguard), meta=(BlueprintSpawnableComponent))
class SKYGUARD52_API USkyguardPauseHostComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	USkyguardPauseHostComponent();

	virtual void BeginPlay() override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Pause")
	void TogglePause();

	bool BindPauseInput(UInputComponent* InputComponent);

	UFUNCTION(BlueprintPure, Category="Skyguard|Pause")
	bool IsPauseMenuVisible() const;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Pause")
	TSoftClassPtr<USkyguardPauseSettingsWidget> PauseWidgetClass;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Pause")
	int32 PauseWidgetZOrder = 100;

private:
	UPROPERTY(Transient)
	TObjectPtr<USkyguardPauseSettingsWidget> ActiveWidget;

	TWeakObjectPtr<UInputComponent> BoundInputComponent;

	APlayerController* ResolvePlayerController() const;
	void ResumeGame(APlayerController* PlayerController);
};
