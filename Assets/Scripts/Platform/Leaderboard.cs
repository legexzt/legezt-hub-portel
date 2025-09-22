using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;

public class Leaderboard : MonoBehaviour
{
    public Text leaderboardText;

    void Start()
    {
        DisplayLeaderboard();
    }

    void DisplayLeaderboard()
    {
        Dictionary<string, int> scores = new Dictionary<string, int>();
        scores["ShadowRunner"] = PlayerPrefs.GetInt("ShadowRunner_HighScore", 0);
        scores["GravitySwitchArena"] = PlayerPrefs.GetInt("GravitySwitchArena_HighScore", 0);
        scores["TimeLoopQuest"] = PlayerPrefs.GetInt("TimeLoopQuest_HighScore", 0);
        scores["ElementalClash"] = PlayerPrefs.GetInt("ElementalClash_HighScore", 0);
        scores["NanoBotsWar"] = PlayerPrefs.GetInt("NanoBotsWar_HighScore", 0);

        leaderboardText.text = "Leaderboard:\n";
        foreach (var score in scores)
        {
            leaderboardText.text += score.Key + ": " + score.Value + "\n";
        }
    }

    public void OnBackButton()
    {
        SceneManager.LoadScene("MainMenu");
    }
}