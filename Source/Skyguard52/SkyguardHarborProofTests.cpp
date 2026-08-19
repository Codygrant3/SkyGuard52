#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCampaignRoster.h"
#include "SkyguardGunshipSortieDirector.h"
#include "SkyguardRadarNode.h"
#include "Engine/World.h"
#include "GameFramework/InputSettings.h"
#include "InputCoreTypes.h"
#include "Misc/AutomationTest.h"
#include "Misc/Char.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

namespace SkyguardHarborProofTests
{
	constexpr float HarborProofBeats[7] = {
		120.f, 240.f, 360.f, 480.f, 600.f, 780.f, 900.f};

	bool BeatsMatchProof(const float BeatSeconds[7])
	{
		for (int32 Index = 0; Index < 7; ++Index)
		{
			if (!FMath::IsNearlyEqual(
					BeatSeconds[Index], HarborProofBeats[Index], 0.01f))
			{
				return false;
			}
		}
		return true;
	}

	bool FindPopFlaresIniKey(const FString& IniText, FString& OutKey)
	{
		OutKey.Reset();
		const FString Needle = TEXT("ActionName=\"PopFlares\"");
		const int32 LineStart = IniText.Find(Needle, ESearchCase::CaseSensitive);
		if (LineStart == INDEX_NONE)
		{
			return false;
		}

		const int32 LineEnd = IniText.Find(
			TEXT("\n"),
			ESearchCase::CaseSensitive,
			ESearchDir::FromStart,
			LineStart);
		const FString Line = LineEnd == INDEX_NONE
			? IniText.Mid(LineStart)
			: IniText.Mid(LineStart, LineEnd - LineStart);

		const FString KeyToken = TEXT("Key=");
		const int32 KeyPos = Line.Find(KeyToken, ESearchCase::CaseSensitive);
		if (KeyPos == INDEX_NONE)
		{
			return false;
		}

		FString Key = Line.Mid(KeyPos + KeyToken.Len());
		Key.TrimStartAndEndInline();
		while (Key.Len() > 0 &&
			(Key[Key.Len() - 1] == TEXT(')') ||
				FChar::IsWhitespace(Key[Key.Len() - 1])))
		{
			Key.LeftChopInline(1);
		}
		OutKey = Key;
		return true;
	}

	bool GunnerBindsPopFlares(const FString& GunnerCpp)
	{
		return GunnerCpp.Contains(
			TEXT("BindAction(TEXT(\"PopFlares\")"),
			ESearchCase::CaseSensitive);
	}

	UWorld* MakeWorld(const TCHAR* Name)
	{
		return UWorld::CreateWorld(EWorldType::Game, false, Name);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardHarborProofExtractClockTest,
	"Skyguard52.HarborProof.ExtractClock",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardHarborProofExtractClockTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardHarborProofTests;

	const FSkyguardCampaignMissionSpec& Harbor = SkyguardCampaignRoster::Get(1);
	TestEqual(
		TEXT("harbor id is M02"),
		Harbor.MissionId,
		FName(TEXT("M02_HarborShield")));
	TestEqual(
		TEXT("harbor title stays Harbor Breaker"),
		FString(Harbor.Title),
		FString(TEXT("Harbor Breaker")));
	TestTrue(
		TEXT("Harbor roster stays on the 15-minute proof clock"),
		BeatsMatchProof(Harbor.BeatSeconds));
	TestTrue(
		TEXT("extract ends at 15 min (900s)"),
		FMath::IsNearlyEqual(Harbor.BeatSeconds[6], 900.f, 0.01f));
	TestTrue(
		TEXT("extract starts at 13 min (780s)"),
		FMath::IsNearlyEqual(Harbor.BeatSeconds[5], 780.f, 0.01f));

	UWorld* World = MakeWorld(TEXT("SkyguardHarborProofExtractClockWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardGunshipSortieDirector* Director =
		World->SpawnActor<ASkyguardGunshipSortieDirector>();
	TestNotNull(TEXT("director"), Director);
	if (!Director)
	{
		World->DestroyWorld(false);
		return false;
	}

	Director->bAutoStart = false;
	Director->StartMissionIndex(1);
	TestEqual(
		TEXT("harbor starts on approach"),
		Director->GetBeat(),
		ESkyguardSortieBeat::Approach);

	// AdvanceBeats moves one gate per Tick. 2/4/6/8/10/13 min.
	Director->Tick(120.f);
	TestEqual(
		TEXT("2 min is contact"),
		Director->GetBeat(),
		ESkyguardSortieBeat::InitialContact);
	Director->Tick(120.f);
	TestEqual(
		TEXT("4 min is shore"),
		Director->GetBeat(),
		ESkyguardSortieBeat::ShoreAssault);
	Director->Tick(120.f);
	TestEqual(
		TEXT("6 min is radar net"),
		Director->GetBeat(),
		ESkyguardSortieBeat::RadarNet);
	Director->Tick(120.f);
	TestEqual(
		TEXT("8 min is choice"),
		Director->GetBeat(),
		ESkyguardSortieBeat::Choice);
	Director->Tick(120.f);
	TestEqual(
		TEXT("10 min is climax"),
		Director->GetBeat(),
		ESkyguardSortieBeat::Climax);
	Director->Tick(180.f);
	TestEqual(
		TEXT("13 min opens extract, not win"),
		Director->GetBeat(),
		ESkyguardSortieBeat::Extraction);
	TestFalse(
		TEXT("extract clock is still running at 13 min"),
		Director->IsSortieOver());

	Director->Tick(119.f);
	TestEqual(
		TEXT("14:59 is still extract"),
		Director->GetBeat(),
		ESkyguardSortieBeat::Extraction);
	TestFalse(
		TEXT("extract does not win before 15 min"),
		Director->IsSortieOver());

	Director->Tick(1.f);
	TestEqual(
		TEXT("15 min extract clock resolves a win"),
		Director->GetBeat(),
		ESkyguardSortieBeat::Succeeded);
	TestTrue(
		TEXT("sortie is over at 15 min"),
		Director->IsSortieOver());

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardHarborProofRadarDownLengthensInboundTest,
	"Skyguard52.HarborProof.RadarDownLengthensInbound",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardHarborProofRadarDownLengthensInboundTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardHarborProofTests;

	const float Live =
		ASkyguardGunshipSortieDirector::IncomingIntervalSeconds(true);
	const float Down =
		ASkyguardGunshipSortieDirector::IncomingIntervalSeconds(false);
	TestEqual(
		TEXT("radar-live uses the named live interval"),
		Live,
		static_cast<double>(
			ASkyguardGunshipSortieDirector::IncomingRadarLiveIntervalSeconds));
	TestEqual(
		TEXT("radar-down uses the named down interval"),
		Down,
		static_cast<double>(
			ASkyguardGunshipSortieDirector::IncomingRadarDownIntervalSeconds));
	TestTrue(
		TEXT("radar-down lengthens inbound vs radar-live"),
		Down > Live);
	TestEqual(
		TEXT("radar-net with a live shore net uses the live clock"),
		ASkyguardGunshipSortieDirector::IncomingIntervalSecondsForNet(
			ESkyguardSortieBeat::RadarNet, true, false),
		static_cast<double>(Live));
	TestEqual(
		TEXT("radar-net with the shore net down uses the down clock"),
		ASkyguardGunshipSortieDirector::IncomingIntervalSecondsForNet(
			ESkyguardSortieBeat::RadarNet, false, false),
		static_cast<double>(Down));

	UWorld* World = MakeWorld(TEXT("SkyguardHarborProofRadarDownWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardGunshipSortieDirector* Director =
		World->SpawnActor<ASkyguardGunshipSortieDirector>();
	TestNotNull(TEXT("director"), Director);
	if (!Director)
	{
		World->DestroyWorld(false);
		return false;
	}

	Director->bAutoStart = false;
	Director->StartMissionIndex(1);
	Director->Tick(120.f);
	Director->Tick(120.f);
	Director->Tick(120.f);
	TestEqual(
		TEXT("harbor is on radar-net"),
		Director->GetBeat(),
		ESkyguardSortieBeat::RadarNet);

	ASkyguardRadarNode* ShoreRadar = Director->GetRadarNode();
	TestNotNull(TEXT("harbor radar node"), ShoreRadar);
	if (!ShoreRadar)
	{
		World->DestroyWorld(false);
		return false;
	}
	TestFalse(TEXT("shore radar starts live"), ShoreRadar->IsDestroyed());
	TestEqual(
		TEXT("live harbor radar uses the live inbound interval"),
		Director->ResolveIncomingIntervalSeconds(),
		static_cast<double>(Live));

	ShoreRadar->ApplyDamage(500.f);
	TestTrue(TEXT("shore radar is down"), ShoreRadar->IsDestroyed());
	TestEqual(
		TEXT("killing harbor radar lengthens inbound"),
		Director->ResolveIncomingIntervalSeconds(),
		static_cast<double>(Down));
	TestTrue(
		TEXT("resolved radar-down interval is longer than live"),
		Director->ResolveIncomingIntervalSeconds() > Live);

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardHarborProofPopFlaresMappedToKeyXTest,
	"Skyguard52.HarborProof.PopFlaresMappedToKeyX",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardHarborProofPopFlaresMappedToKeyXTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardHarborProofTests;

	const FString IniPath = FPaths::ProjectConfigDir() / TEXT("DefaultInput.ini");
	FString IniText;
	const bool bLoadedIni = FFileHelper::LoadFileToString(IniText, *IniPath);
	TestTrue(TEXT("DefaultInput.ini is readable"), bLoadedIni);
	if (!bLoadedIni)
	{
		return false;
	}

	FString IniKey;
	TestTrue(
		TEXT("PopFlares mapping exists in DefaultInput.ini"),
		FindPopFlaresIniKey(IniText, IniKey));
	TestEqual(TEXT("PopFlares ini key is X"), IniKey, FString(TEXT("X")));
	TestTrue(
		TEXT("PopFlares line contains Key=X"),
		IniText.Contains(
			TEXT("ActionName=\"PopFlares\""),
			ESearchCase::CaseSensitive) &&
			IniText.Contains(TEXT("Key=X"), ESearchCase::CaseSensitive));

	const FString GunnerPath =
		FPaths::ProjectDir() / TEXT("Source/Skyguard52/SkyguardGunner.cpp");
	FString GunnerCpp;
	TestTrue(
		TEXT("SkyguardGunner.cpp is readable"),
		FFileHelper::LoadFileToString(GunnerCpp, *GunnerPath));
	TestTrue(
		TEXT("gunner binds PopFlares"),
		GunnerBindsPopFlares(GunnerCpp));

	const UInputSettings* Settings = GetDefault<UInputSettings>();
	TestNotNull(TEXT("UInputSettings"), Settings);
	if (!Settings)
	{
		return false;
	}

	TArray<FInputActionKeyMapping> Mappings;
	Settings->GetActionMappingByName(TEXT("PopFlares"), Mappings);
	TestTrue(TEXT("runtime PopFlares mapping exists"), Mappings.Num() > 0);
	bool bHasX = false;
	bool bHasC = false;
	for (const FInputActionKeyMapping& Mapping : Mappings)
	{
		bHasX |= Mapping.Key == EKeys::X;
		bHasC |= Mapping.Key == EKeys::C;
	}
	TestTrue(TEXT("runtime PopFlares includes Key X"), bHasX);
	TestFalse(TEXT("runtime PopFlares does not include Key C"), bHasC);
	return true;
}

#endif
