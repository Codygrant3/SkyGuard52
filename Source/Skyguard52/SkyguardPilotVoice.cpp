#include "SkyguardPilotVoice.h"

#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"

namespace
{
	ESkyguardPilotLine GLastCalledLine = ESkyguardPilotLine::RadarLit;
	FString GLastCalledText;
	int32 GCalledEventCount = 0;

	void Say(UObject* WorldContext, const TCHAR* Line, const float Seconds)
	{
		if (!GEngine || !WorldContext || !WorldContext->GetWorld())
		{
			return;
		}
		GEngine->AddOnScreenDebugMessage(
			84711,
			Seconds,
			FLinearColor(1.f, 0.82f, 0.35f).ToFColor(true),
			FString::Printf(TEXT("PILOT: %s"), Line));
	}

	void TryEnqueue(
		UObject* WorldContext,
		const ESkyguardPilotLine Line)
	{
		const AActor* Actor = Cast<AActor>(WorldContext);
		if (!Actor)
		{
			return;
		}
		if (USkyguardRadioChatterComponent* Radio =
			Actor->FindComponentByClass<USkyguardRadioChatterComponent>())
		{
			Radio->EnqueueLine(SkyguardPilotVoice::MakeRadioLine(Line));
		}
	}
}

FString SkyguardPilotVoice::LineTextForEvent(const ESkyguardPilotLine Line)
{
	switch (Line)
	{
	case ESkyguardPilotLine::RadarLit:
		return TEXT("Radar just lit us. ADA is going to get faster.");
	case ESkyguardPilotLine::CargoHit:
		return TEXT("Cargo is taking hits. Prioritize the inbound.");
	case ESkyguardPilotLine::CargoCritical:
		return TEXT("That hull is on fire. We lose it, we lose the sortie.");
	case ESkyguardPilotLine::ShipRadarDown:
		return TEXT("Their search radar is down. Window is ours.");
	case ESkyguardPilotLine::ShipEnginesDown:
		return TEXT("Engines killed. She's dead in the water.");
	case ESkyguardPilotLine::ShipLauncherDown:
		return TEXT("Launcher cold. No more inbound from that hull.");
	case ESkyguardPilotLine::ShipCannonDown:
		return TEXT("Their cannon is scrap. Close if you want.");
	case ESkyguardPilotLine::ShipDeckDown:
		return TEXT("Drone deck is burning. No more rotors off that ship.");
	case ESkyguardPilotLine::ShipDead:
		return TEXT("Patrol ship is a hulk. Nice work.");
	case ESkyguardPilotLine::Inbound:
		return TEXT("Missile inbound — flares!");
	case ESkyguardPilotLine::FlaresGood:
		return TEXT("Flares good. Break.");
	case ESkyguardPilotLine::Choice:
		return TEXT("Your call — kill that radar or stay on the ship.");
	case ESkyguardPilotLine::Extract:
		return TEXT("Extract. Get out of the glass.");
	case ESkyguardPilotLine::GoThermal:
		return TEXT("Blackout. Thermal. Don't hose the dark blocks.");
	case ESkyguardPilotLine::Win:
		return TEXT("We're Winchester-safe. Coming home.");
	case ESkyguardPilotLine::Fail:
		return TEXT("That's a loss. We go back in or we go home.");
	case ESkyguardPilotLine::LoadoutPrompt:
		return TEXT("Pick a loadout. One armor, two rockets, three intercept, four balanced.");
	default:
		return FString();
	}
}

float SkyguardPilotVoice::LineDurationForEvent(const ESkyguardPilotLine Line)
{
	switch (Line)
	{
	case ESkyguardPilotLine::RadarLit:
	case ESkyguardPilotLine::CargoCritical:
	case ESkyguardPilotLine::Choice:
	case ESkyguardPilotLine::GoThermal:
		return 3.2f;
	case ESkyguardPilotLine::Win:
	case ESkyguardPilotLine::Fail:
		return 3.0f;
	case ESkyguardPilotLine::CargoHit:
	case ESkyguardPilotLine::ShipRadarDown:
	case ESkyguardPilotLine::ShipEnginesDown:
	case ESkyguardPilotLine::ShipLauncherDown:
	case ESkyguardPilotLine::ShipDeckDown:
	case ESkyguardPilotLine::ShipDead:
	case ESkyguardPilotLine::Extract:
		return 2.8f;
	case ESkyguardPilotLine::Inbound:
	case ESkyguardPilotLine::ShipCannonDown:
		return 2.6f;
	case ESkyguardPilotLine::FlaresGood:
		return 2.0f;
	case ESkyguardPilotLine::LoadoutPrompt:
		return 4.0f;
	default:
		return 2.4f;
	}
}

FSkyguardRadioLine SkyguardPilotVoice::MakeRadioLine(const ESkyguardPilotLine Line)
{
	FSkyguardRadioLine RadioLine;
	switch (Line)
	{
	case ESkyguardPilotLine::RadarLit:
		RadioLine.LineId = TEXT("RadarLit");
		RadioLine.Priority = 80;
		break;
	case ESkyguardPilotLine::Inbound:
		RadioLine.LineId = TEXT("Inbound");
		RadioLine.Priority = 100;
		break;
	case ESkyguardPilotLine::Choice:
		RadioLine.LineId = TEXT("Choice");
		RadioLine.Priority = 75;
		break;
	case ESkyguardPilotLine::Extract:
		RadioLine.LineId = TEXT("Extract");
		RadioLine.Priority = 70;
		break;
	case ESkyguardPilotLine::GoThermal:
		RadioLine.LineId = TEXT("GoThermal");
		RadioLine.Priority = 85;
		break;
	case ESkyguardPilotLine::FlaresGood:
		RadioLine.LineId = TEXT("FlaresGood");
		RadioLine.Priority = 90;
		break;
	case ESkyguardPilotLine::Win:
		RadioLine.LineId = TEXT("Win");
		RadioLine.Priority = 60;
		break;
	case ESkyguardPilotLine::Fail:
		RadioLine.LineId = TEXT("Fail");
		RadioLine.Priority = 60;
		break;
	default:
		RadioLine.LineId = TEXT("PilotLine");
		RadioLine.Priority = 50;
		break;
	}
	RadioLine.Speaker = FText::FromString(TEXT("PILOT"));
	RadioLine.Subtitle = FText::FromString(LineTextForEvent(Line));
	RadioLine.EstimatedDurationSeconds = LineDurationForEvent(Line);
	RadioLine.CooldownSeconds = 0.f;
	return RadioLine;
}

void SkyguardPilotVoice::ConfirmCommand(
	UObject* WorldContext,
	const ESkyguardPilotCommand Command)
{
	switch (Command)
	{
	case ESkyguardPilotCommand::OrbitLeft:
		Say(WorldContext, TEXT("Coming left. Holding the circle."), 2.6f);
		break;
	case ESkyguardPilotCommand::OrbitRight:
		Say(WorldContext, TEXT("Coming right. Holding the circle."), 2.6f);
		break;
	case ESkyguardPilotCommand::AttackRun:
		Say(WorldContext, TEXT("Rolling in."), 2.2f);
		break;
	case ESkyguardPilotCommand::Break:
		Say(WorldContext, TEXT("Breaking off."), 2.2f);
		break;
	case ESkyguardPilotCommand::Extend:
		Say(WorldContext, TEXT("Opening the range."), 2.2f);
		break;
	case ESkyguardPilotCommand::Hold:
		Say(WorldContext, TEXT("Holding station."), 2.2f);
		break;
	case ESkyguardPilotCommand::Climb:
		Say(WorldContext, TEXT("Popping up."), 2.2f);
		break;
	case ESkyguardPilotCommand::Descend:
		Say(WorldContext, TEXT("Dropping behind cover."), 2.2f);
		break;
	case ESkyguardPilotCommand::FaceTarget:
		Say(WorldContext, TEXT("Coming onto your target."), 2.4f);
		break;
	case ESkyguardPilotCommand::Pursuit:
	default:
		Say(WorldContext, TEXT("Staying in the fight."), 2.2f);
		break;
	}
}

void SkyguardPilotVoice::WarnOffAxis(UObject* WorldContext)
{
	Say(WorldContext, TEXT("Break the glass — threat off your sensor."), 3.2f);
}

void SkyguardPilotVoice::CallLock(UObject* WorldContext)
{
	Say(WorldContext, TEXT("Good lock. Missile is yours."), 2.4f);
}

void SkyguardPilotVoice::CallReload(UObject* WorldContext, const TCHAR* Station)
{
	Say(
		WorldContext,
		*FString::Printf(TEXT("Reloading %s."), Station ? Station : TEXT("guns")),
		2.2f);
}

void SkyguardPilotVoice::CallEvent(
	UObject* WorldContext,
	const ESkyguardPilotLine Line)
{
	const FString Text = LineTextForEvent(Line);
	if (Text.IsEmpty())
	{
		return;
	}
	GLastCalledLine = Line;
	GLastCalledText = Text;
	++GCalledEventCount;
	Say(WorldContext, *Text, LineDurationForEvent(Line));
	TryEnqueue(WorldContext, Line);
}

void SkyguardPilotVoice::ResetCallProbe()
{
	GLastCalledLine = ESkyguardPilotLine::RadarLit;
	GLastCalledText.Reset();
	GCalledEventCount = 0;
}

ESkyguardPilotLine SkyguardPilotVoice::GetLastCalledLine()
{
	return GLastCalledLine;
}

FString SkyguardPilotVoice::GetLastCalledText()
{
	return GLastCalledText;
}

int32 SkyguardPilotVoice::GetCalledEventCount()
{
	return GCalledEventCount;
}
