using UnityEngine;
using UnityEngine.SceneManagement;

public class GameLibrary : MonoBehaviour
{
    public void OnShadowRunnerButton()
    {
        SceneManager.LoadScene("ShadowRunner_Start");
    }

    public void OnGravitySwitchArenaButton()
    {
        SceneManager.LoadScene("GravitySwitchArena_Start");
    }

    public void OnTimeLoopQuestButton()
    {
        SceneManager.LoadScene("TimeLoopQuest_Start");
    }

    public void OnElementalClashButton()
    {
        SceneManager.LoadScene("ElementalClash_Start");
    }

    public void OnNanoBotsWarButton()
    {
        SceneManager.LoadScene("NanoBotsWar_Start");
    }

    public void OnBackButton()
    {
        SceneManager.LoadScene("MainMenu");
    }
}