#include "SkyguardCpgSightHud.h"

#include "SkyguardCpgHud.h"
#include "SkyguardGunner.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "Rendering/DrawElements.h"
#include "Rendering/SlateLayoutTransform.h"
#include "Styling/CoreStyle.h"

void USkyguardCpgSightHud::BindGunner(ASkyguardGunner* InGunner)
{
	Gunner = InGunner;
}

void USkyguardCpgSightHud::NativeTick(const FGeometry& MyGeometry, const float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);
	ASkyguardGunner* Live = Gunner.Get();
	Marks.Reset();
	if (!Live)
	{
		return;
	}
	Cached = Live->BuildCpgHudSnapshot();
	bSight = Live->IsCpgSightActive();
	const int32 Center = FMath::RoundToInt(Cached.HeadingDegrees);
	HeadingTape = FString::Printf(
		TEXT("%03d   %03d   %03d"),
		(Center + 357) % 360,
		Center,
		(Center + 3) % 360);

	APlayerController* PC = Cast<APlayerController>(Live->GetController());
	if (!PC && Live->GetWorld())
	{
		PC = Live->GetWorld()->GetFirstPlayerController();
	}
	if (!PC)
	{
		return;
	}

	TArray<FSkyguardCpgContactMark> WorldMarks;
	Live->CollectCpgContactMarks(WorldMarks);
	for (const FSkyguardCpgContactMark& WorldMark : WorldMarks)
	{
		FVector2D Screen;
		if (!PC->ProjectWorldLocationToScreen(WorldMark.WorldLocation, Screen, true))
		{
			continue;
		}
		FScreenMark Mark;
		Mark.Screen = Screen;
		Mark.Label = WorldMark.Label;
		Mark.bLocked = WorldMark.bLocked;
		Mark.bSeeking = WorldMark.bSeeking;
		const float Dist = FVector::Dist(
			Live->GetActorLocation(),
			WorldMark.WorldLocation);
		Mark.Size = FMath::Clamp(22000.f / FMath::Max(Dist, 400.f) * 36.f, 18.f, 72.f);
		if (WorldMark.bSeeking)
		{
			Mark.Size *= FMath::Lerp(1.35f, 0.85f, WorldMark.LockAlpha);
		}
		Marks.Add(Mark);
	}
}

int32 USkyguardCpgSightHud::NativePaint(
	const FPaintArgs& Args,
	const FGeometry& AllottedGeometry,
	const FSlateRect& MyCullingRect,
	FSlateWindowElementList& OutDrawElements,
	int32 LayerId,
	const FWidgetStyle& InWidgetStyle,
	const bool bParentEnabled) const
{
	int32 Layer = Super::NativePaint(
		Args,
		AllottedGeometry,
		MyCullingRect,
		OutDrawElements,
		LayerId,
		InWidgetStyle,
		bParentEnabled);

	const FVector2D Size = AllottedGeometry.GetLocalSize();
	if (Size.X < 8.f || Size.Y < 8.f)
	{
		return Layer;
	}

	const FPaintGeometry Paint = AllottedGeometry.ToPaintGeometry();
	const FSlateBrush* Brush = FCoreStyle::Get().GetBrush("WhiteBrush");
	const FLinearColor Frame(0.03f, 0.03f, 0.035f, 0.94f);
	const FLinearColor Seal(0.18f, 0.85f, 0.28f, 0.35f);
	const FLinearColor Green(0.25f, 1.f, 0.35f, 0.9f);
	const FLinearColor Lock(1.f, 0.85f, 0.2f, 0.95f);
	const FLinearColor Seek(0.35f, 1.f, 0.55f, 0.7f);

	const float Side = FMath::Clamp(Size.X * 0.05f, 32.f, 64.f);
	const float Top = FMath::Clamp(Size.Y * 0.06f, 28.f, 52.f);
	const float Bottom = FMath::Clamp(Size.Y * 0.045f, 22.f, 40.f);
	if (Brush)
	{
		auto Fill = [&](float X, float Y, float W, float H, const FLinearColor& Color)
		{
			FSlateDrawElement::MakeBox(
				OutDrawElements,
				Layer,
				AllottedGeometry.ToPaintGeometry(
					FVector2f(W, H),
					FSlateLayoutTransform(FVector2f(X, Y))),
				Brush,
				ESlateDrawEffect::None,
				Color);
		};
		Fill(0.f, 0.f, Side, Size.Y, Frame);
		Fill(Size.X - Side, 0.f, Side, Size.Y, Frame);
		Fill(0.f, 0.f, Size.X, Top, Frame);
		Fill(0.f, Size.Y - Bottom, Size.X, Bottom, Frame);
	}

	auto Line = [&](const FVector2D& A, const FVector2D& B, const FLinearColor& Color, float Thick)
	{
		TArray<FVector2D> Pts;
		Pts.Add(A);
		Pts.Add(B);
		FSlateDrawElement::MakeLines(
			OutDrawElements,
			Layer + 1,
			Paint,
			Pts,
			ESlateDrawEffect::None,
			Color,
			true,
			Thick);
	};

	Line(FVector2D(Side, Top), FVector2D(Size.X - Side, Top), Seal, 1.2f);
	Line(FVector2D(Side, Size.Y - Bottom), FVector2D(Size.X - Side, Size.Y - Bottom), Seal, 1.2f);
	Line(FVector2D(Side, Top), FVector2D(Side, Size.Y - Bottom), Seal, 1.2f);
	Line(FVector2D(Size.X - Side, Top), FVector2D(Size.X - Side, Size.Y - Bottom), Seal, 1.2f);

	const FSlateFontInfo Font = FCoreStyle::GetDefaultFontStyle("Regular", 15);
	auto Text = [&](const FString& Value, const FVector2D& Pos, const FLinearColor& Color)
	{
		FSlateDrawElement::MakeText(
			OutDrawElements,
			Layer + 2,
			AllottedGeometry.ToPaintGeometry(
				FVector2f(420.f, 44.f),
				FSlateLayoutTransform(FVector2f(Pos))),
			Value,
			Font,
			ESlateDrawEffect::None,
			Color);
	};

	if (!bSight)
	{
		return Layer + 3;
	}

	const FVector2D Center = Size * 0.5f;
	const float Arm = 28.f;
	const float Gap = 8.f;
	Line(FVector2D(Center.X - Arm, Center.Y), FVector2D(Center.X - Gap, Center.Y), Green, 1.4f);
	Line(FVector2D(Center.X + Gap, Center.Y), FVector2D(Center.X + Arm, Center.Y), Green, 1.4f);
	Line(FVector2D(Center.X, Center.Y - Arm), FVector2D(Center.X, Center.Y - Gap), Green, 1.4f);
	Line(FVector2D(Center.X, Center.Y + Gap), FVector2D(Center.X, Center.Y + Arm), Green, 1.4f);

	const TCHAR* Weapon = SkyguardCpgWeaponLabel(
		Gunner.IsValid()
			? Gunner->GetSelectedGunshipWeapon()
			: ESkyguardGunshipWeapon::Cannon);
	const FString Range = Cached.RangeMeters < 0.f
		? FString(TEXT("RNG ----"))
		: FString::Printf(TEXT("RNG %.0f"), Cached.RangeMeters);
	Text(FString::Printf(TEXT("%s  RDY"), Weapon), FVector2D(Side + 16.f, Top + 10.f), Green);
	Text(Range, FVector2D(Size.X - Side - 160.f, Top + 10.f), Green);
	Text(HeadingTape, FVector2D(Center.X - 70.f, Top + 8.f), Green);

	if (Cached.ThreatCount > 0)
	{
		Text(
			FString::Printf(TEXT("%d THRT"), Cached.ThreatCount),
			FVector2D(Size.X - Side - 160.f, Size.Y - Bottom - 28.f),
			Green);
	}

	for (const FScreenMark& Mark : Marks)
	{
		const FLinearColor Color = Mark.bLocked ? Lock : (Mark.bSeeking ? Seek : Green);
		const float Half = Mark.Size * 0.5f;
		const FVector2D P = Mark.Screen;
		if (P.X < Side || P.X > Size.X - Side || P.Y < Top || P.Y > Size.Y - Bottom)
		{
			continue;
		}
		const float Corner = FMath::Max(6.f, Half * 0.35f);
		const FVector2D TL(P.X - Half, P.Y - Half);
		const FVector2D TR(P.X + Half, P.Y - Half);
		const FVector2D BL(P.X - Half, P.Y + Half);
		const FVector2D BR(P.X + Half, P.Y + Half);
		if (Mark.bLocked)
		{
			Line(TL, TR, Color, 2.f);
			Line(TR, BR, Color, 2.f);
			Line(BR, BL, Color, 2.f);
			Line(BL, TL, Color, 2.f);
			Text(TEXT("LCK"), FVector2D(P.X - 16.f, P.Y - Half - 18.f), Color);
		}
		else
		{
			Line(TL, FVector2D(TL.X + Corner, TL.Y), Color, 1.5f);
			Line(TL, FVector2D(TL.X, TL.Y + Corner), Color, 1.5f);
			Line(TR, FVector2D(TR.X - Corner, TR.Y), Color, 1.5f);
			Line(TR, FVector2D(TR.X, TR.Y + Corner), Color, 1.5f);
			Line(BL, FVector2D(BL.X + Corner, BL.Y), Color, 1.5f);
			Line(BL, FVector2D(BL.X, BL.Y - Corner), Color, 1.5f);
			Line(BR, FVector2D(BR.X - Corner, BR.Y), Color, 1.5f);
			Line(BR, FVector2D(BR.X, BR.Y - Corner), Color, 1.5f);
		}
		if (!Mark.Label.IsEmpty())
		{
			Text(Mark.Label, FVector2D(P.X + Half + 4.f, P.Y - 8.f), Color);
		}
	}

	return Layer + 3;
}
