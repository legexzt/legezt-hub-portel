using UnityEngine;

public class ElementalFighter : MonoBehaviour
{
    public enum Element { Fire, Water, Earth, Air }
    public Element currentElement;

    public void SwitchElement(Element newElement)
    {
        currentElement = newElement;
        // Change abilities
    }

    public void Attack()
    {
        // Perform attack based on element
        switch (currentElement)
        {
            case Element.Fire:
                // Fire attack
                break;
            case Element.Water:
                // Water attack
                break;
            case Element.Earth:
                // Earth attack
                break;
            case Element.Air:
                // Air attack
                break;
        }
    }
}