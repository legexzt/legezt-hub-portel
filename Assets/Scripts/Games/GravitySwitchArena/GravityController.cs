using UnityEngine;

public class GravityController : MonoBehaviour
{
    public float gravityStrength = 9.81f;
    private bool gravityFlipped = false;

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.G))
        {
            FlipGravity();
        }
    }

    void FlipGravity()
    {
        gravityFlipped = !gravityFlipped;
        Physics.gravity = gravityFlipped ? Vector3.up * gravityStrength : Vector3.down * gravityStrength;
        // Rotate player or world
        transform.Rotate(180, 0, 0);
    }
}