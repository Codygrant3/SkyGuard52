#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "SkyguardCpgHud.h"
#include "SkyguardCpgSightHud.generated.h"

class ASkyguardGunner;

/** Screen overlay for looking *through* TEDAC/TADS. Imagine-concept layout only. */
UCLASS()
class SKYGUARD52_API USkyguardCpgSightHud : public UUserWidget
{
	GENERATED_BODY()

public:
	void BindGunner(ASkyguardGunner* InGunner);

protected:
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;
	virtual int32 NativePaint(
		const FPaintArgs& Args,
		const FGeometry& AllottedGeometry,
		const FSlateRect& MyCullingRect,
		FSlateWindowElementList& OutDrawElements,
		int32 LayerId,
		const FWidgetStyle& InWidgetStyle,
		bool bParentEnabled) const override;

private:
	struct FScreenMark
	{
		FVector2D Screen = FVector2D::ZeroVector;
		FString Label;
		float Size = 28.f;
		bool bLocked = false;
		bool bSeeking = false;
	};

	TWeakObjectPtr<ASkyguardGunner> Gunner;
	FSkyguardCpgHudSnapshot Cached;
	TArray<FScreenMark> Marks;
	FString HeadingTape;
	bool bSight = false;
};
