/*
Simple Blocks based visualization unit for chintan

Scope : Just positive number along with non-decimal values support along with range of 100 as the maximum number to load for visualization

  For decimal it would be giving explanation or graph based handle would work good, rather then loading with blocks
*/ 

export function initCanvas(canvasElement){
  if (!canvasElement) return;
  const ctx = canvasElement.getContext('2d');

  ctx.fillStyle = '#42b883';
  ctx.fillRect(10,10,150,100);
}
