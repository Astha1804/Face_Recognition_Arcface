export const sendFrameForRecognition = async (imageData) => {
  const response = await fetch("http://localhost:5000/recognize", {
    method: "POST",
    body: imageData
  });
  return response.json();
};
