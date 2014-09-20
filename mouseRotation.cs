using UnityEngine;
using System.Collections;

public class mouseRotation : MonoBehaviour {

	public enum RotationAxes { MouseXAndY = 0, MouseX = 1, MouseY = 2 }
	public RotationAxes axes = RotationAxes.MouseXAndY;
	public float sensitivityX = 5F;
	public float sensitivityY = 5F;

	public float minimumX = -30F;
	public float maximumX = 30F;

	public float minimumY = -10F;
	public float maximumY = 10F;

	float rotationY = 0F;
	float rotationX = 0F;
	
	void Update ()
	{
		if (axes == RotationAxes.MouseX || axes == RotationAxes.MouseXAndY)
		{
			rotationX += Input.GetAxis("Mouse X") * sensitivityX;
			rotationX = Mathf.Clamp (rotationX, minimumX, maximumX);
			rotationY += Input.GetAxis("Mouse Y") * sensitivityY;
			rotationY = Mathf.Clamp (rotationY, minimumY, maximumY);
			
			transform.localEulerAngles = new Vector3(-rotationY,rotationX, 0);
		}

	}
}
