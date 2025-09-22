using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

public class Settings : MonoBehaviour
{
    public Slider volumeSlider;
    public Dropdown qualityDropdown;

    void Start()
    {
        // Load current settings
        volumeSlider.value = PlayerPrefs.GetFloat("Volume", 1f);
        qualityDropdown.value = PlayerPrefs.GetInt("Quality", 2);
    }

    public void OnVolumeChange()
    {
        AudioListener.volume = volumeSlider.value;
        PlayerPrefs.SetFloat("Volume", volumeSlider.value);
    }

    public void OnQualityChange()
    {
        QualitySettings.SetQualityLevel(qualityDropdown.value);
        PlayerPrefs.SetInt("Quality", qualityDropdown.value);
    }

    public void OnBackButton()
    {
        SceneManager.LoadScene("MainMenu");
    }
}