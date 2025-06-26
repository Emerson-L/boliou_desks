# Boliou Desk Vandalism Tapestry

[Explore it here.](https://emerson-l.github.io/boliou_desks/)

At a school named Carleton in a building named Boliou Hall, there lies an old auditorium with 121 desks. Almost all of the desks sport a smattering of etchings made by distracted students, likely dating back to when the building was renovated in 1995. In my behavioral neuroscience class, my usual desk said "I've fallen and I can't get up," made a statement about the sexuality of one of our ultimate frisbee teams, and firmly demanded that I "TAKE LINGUISTICS!" I wanted to make a collage of all graffiti of students past and present, so I took pictures of all of the desks, manually gathered data on the locations of the desk within those pictures, did some image processing, and put the desks together in a psuedo-tesselation.

<p align="center">
  <img src="https://github.com/user-attachments/assets/39a55e7a-ae29-4f5b-bbe8-7405fc4f94a8" width="500" />
  <img src="https://github.com/user-attachments/assets/ce605004-689c-4638-8d6e-8e733f8287b6" width="251" /> 
</p>
<p align="middle">
  Left: Boliou 104. Right: Taking pictures (with shade!)
</p>

## Process
1. Take a bunch of pictures
2. Gather image data on desk position within the image using `gather_image_quad.py` (made with PyQT5)
3. Calibrate the camera using `calibrate_camera.py` and undistort the images (made with OpenCV)
5. Warp the perspective to the average aspect ratio using `normalize.py` (made with OpenCV)
6. Remove the background (with help from [rembg](https://github.com/danielgatis/rembg))
7. Display desks in a pattern (with help from [svg-pan-zoom](https://github.com/bumbu/svg-pan-zoom))

<p align="middle">
  <img src="https://github.com/user-attachments/assets/c844a06f-9779-4091-9bcd-d72e05ad51cc" width="400" />
</p>
<p align="middle">
  Raw &#8594; Undistorted &#8594; Warped &#8594; Cropped
</p>

## Disclaimer
I take no responsibility for anything written or drawn on any of these desks. I have yet to find anything that I'd call overt hate speech on them, but also wouldn't say that everything on them is graceful. Similarly, I don't claim to have made any of the art. I'm only collaging what other students have put there themselves.








