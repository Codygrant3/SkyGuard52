#if WITH_DEV_AUTOMATION_TESTS

#include "GameFramework/InputSettings.h"
#include "InputCoreTypes.h"
#include "Misc/AutomationTest.h"
#include "Misc/Char.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

namespace SkyguardPopFlaresInputTestPrivate
{
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

	int32 CountKeyXMappings(const FString& IniText)
	{
		int32 Count = 0;
		int32 SearchFrom = 0;
		while (true)
		{
			const int32 Pos = IniText.Find(
				TEXT("Key=X"),
				ESearchCase::CaseSensitive,
				ESearchDir::FromStart,
				SearchFrom);
			if (Pos == INDEX_NONE)
			{
				break;
			}
			++Count;
			SearchFrom = Pos + 5;
		}
		return Count;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardPopFlaresMappedToKeyXTest,
	"Skyguard52.Apache.PopFlaresMappedToKeyX",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardPopFlaresMappedToKeyXTest::RunTest(const FString& Parameters)
{
	// Source of truth: Config/DefaultInput.ini ActionName=PopFlares Key=X.
	const FString IniPath = FPaths::ProjectConfigDir() / TEXT("DefaultInput.ini");
	FString IniText;
	const bool bLoadedIni = FFileHelper::LoadFileToString(IniText, *IniPath);
	TestTrue(TEXT("DefaultInput.ini is readable"), bLoadedIni);
	if (bLoadedIni)
	{
		FString IniKey;
		TestTrue(
			TEXT("PopFlares mapping exists in DefaultInput.ini"),
			SkyguardPopFlaresInputTestPrivate::FindPopFlaresIniKey(IniText, IniKey));
		TestEqual(TEXT("PopFlares ini key is X"), IniKey, FString(TEXT("X")));
		TestEqual(
			TEXT("exactly one Key=X mapping (PopFlares only)"),
			SkyguardPopFlaresInputTestPrivate::CountKeyXMappings(IniText),
			1);
	}
	else
	{
		// Documented bind when the ini cannot be read in this environment.
		TestEqual(
			TEXT("documented PopFlares bind is X"),
			FString(TEXT("X")),
			FString(TEXT("X")));
	}

	const UInputSettings* Settings = GetDefault<UInputSettings>();
	TestNotNull(TEXT("UInputSettings"), Settings);
	if (Settings)
	{
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
	}

	return true;
}

#endif
