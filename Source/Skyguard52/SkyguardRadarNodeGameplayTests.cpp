#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardRadarNode.h"

#include "Engine/World.h"
#include "Misc/AutomationTest.h"

/**
 * Gameplay recycle tests for ASkyguardRadarNode::ResetNode.
 *
 * Public API on main: ApplyDamage, IsDestroyed, ResetNode, Health, MaxHealth.
 * Health idle value is MaxHealth (constructor and ResetNode). Capture/hack
 * getters are not public on main, so they are not asserted here.
 *
 * Presentation, ProxyFallback, and Preferred catalog bindings belong to
 * SkyguardRadarNodeTests.cpp and are intentionally not covered.
 */

namespace SkyguardRadarNodeGameplayTests
{
	UWorld* MakeWorld(const TCHAR* Name)
	{
		return UWorld::CreateWorld(EWorldType::Game, false, Name);
	}

	void TearDown(UWorld* World)
	{
		if (World)
		{
			World->DestroyWorld(false);
		}
	}

	ASkyguardRadarNode* SpawnNode(UWorld* World)
	{
		FActorSpawnParameters Params;
		Params.SpawnCollisionHandlingOverride =
			ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
		return World->SpawnActor<ASkyguardRadarNode>(
			ASkyguardRadarNode::StaticClass(),
			FVector::ZeroVector,
			FRotator::ZeroRotator,
			Params);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardRadarNodeResetRestoresPlayableNodeTest,
	"Skyguard52.RadarNode.Gameplay.ResetRestoresPlayableNode",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRadarNodeResetRestoresPlayableNodeTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardRadarNodeGameplayTests;

	UWorld* World = MakeWorld(TEXT("SkyguardRadarNodeResetPlayableWorld"));
	TestNotNull(TEXT("automation world is created"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardRadarNode* Node = SpawnNode(World);
	TestNotNull(TEXT("radar node spawns"), Node);
	if (!Node)
	{
		TearDown(World);
		return false;
	}

	TestFalse(TEXT("fresh node is not dead"), Node->IsDestroyed());
	TestTrue(
		TEXT("fresh Health is the documented idle value (MaxHealth)"),
		FMath::IsNearlyEqual(Node->Health, Node->MaxHealth));
	TestTrue(
		TEXT("fresh node collision is live"),
		Node->GetActorEnableCollision());

	Node->ApplyDamage(Node->MaxHealth);
	TestTrue(TEXT("lethal damage kills the node"), Node->IsDestroyed());
	TestTrue(
		TEXT("dead Health is at or below idle zero"),
		Node->Health <= 0.f);

	const float DeadHealth = Node->Health;
	Node->ApplyDamage(40.f);
	TestTrue(TEXT("dead node stays dead"), Node->IsDestroyed());
	TestTrue(
		TEXT("dead node ignores further damage (stuck dead)"),
		FMath::IsNearlyEqual(Node->Health, DeadHealth));

	Node->ResetNode();
	TestFalse(TEXT("ResetNode clears dead"), Node->IsDestroyed());
	TestTrue(
		TEXT("ResetNode restores Health to idle MaxHealth"),
		FMath::IsNearlyEqual(Node->Health, Node->MaxHealth));
	TestTrue(
		TEXT("ResetNode restores collision so traces can hit again"),
		Node->GetActorEnableCollision());

	const float AfterReset = Node->Health;
	Node->ApplyDamage(40.f);
	TestFalse(
		TEXT("reset node is not stuck dead"),
		Node->IsDestroyed());
	TestTrue(
		TEXT("reset node accepts damage again"),
		FMath::IsNearlyEqual(Node->Health, AfterReset - 40.f));

	Node->ApplyDamage(Node->MaxHealth);
	TestTrue(
		TEXT("reset node can be killed again"),
		Node->IsDestroyed());

	TearDown(World);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardRadarNodeResetClearsWoundedProgressTest,
	"Skyguard52.RadarNode.Gameplay.ResetClearsWoundedProgress",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRadarNodeResetClearsWoundedProgressTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardRadarNodeGameplayTests;

	UWorld* World = MakeWorld(TEXT("SkyguardRadarNodeResetWoundedWorld"));
	TestNotNull(TEXT("automation world is created"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardRadarNode* Node = SpawnNode(World);
	TestNotNull(TEXT("radar node spawns"), Node);
	if (!Node)
	{
		TearDown(World);
		return false;
	}

	Node->ApplyDamage(50.f);
	TestFalse(TEXT("partial hit leaves the node alive"), Node->IsDestroyed());
	TestTrue(
		TEXT("partial hit lowers Health below idle"),
		Node->Health < Node->MaxHealth);

	Node->ResetNode();
	TestFalse(TEXT("reset after a wound stays alive"), Node->IsDestroyed());
	TestTrue(
		TEXT("reset restores wounded Health to idle MaxHealth"),
		FMath::IsNearlyEqual(Node->Health, Node->MaxHealth));

	TearDown(World);
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
