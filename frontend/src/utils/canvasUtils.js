// 绘制原始图片
export const drawImage = (ctx, dataURL) => {
    const img = new Image()
    img.src = dataURL
    img.onload = () => {
      ctx.drawImage(img, 0, 0, ctx.canvas.width, ctx.canvas.height)
    }
  }
  
// 绘制矢量线段
export const drawInstructions = (ctx, instructions, params) => {
  ctx.strokeStyle = '#000000' // 黑色线段
  ctx.lineWidth = 2

  instructions.forEach(line => {
    const matches = line.match(/arc\(([\d.]+),([\d.]+),([\d.]+),([\d.]+),s,([\d.]+),([\d.]+),0,none,true\)/)
    if (!matches) return
    
    const [time_s, time_e, x1, x2, y1, y2] = matches.slice(1).map(Number)
    
    // 应用坐标变换
    const applyTransformX = (val, origin, scale) => (val - origin) * scale * 400
    const applyTransformY = (val, origin, scale) => ctx.canvas.height - (val - origin) * scale * 400
    
    const transformedX1 = applyTransformX(x1, params.origin_x, params.scale)
    const transformedY1 = applyTransformY(y1, params.origin_y, params.scale)
    const transformedX2 = applyTransformX(x2, params.origin_x, params.scale)
    const transformedY2 = applyTransformY(y2, params.origin_y, params.scale)
    
    // 绘制线段
    ctx.beginPath()
    ctx.moveTo(transformedX1, transformedY1)
    ctx.lineTo(transformedX2, transformedY2)
    ctx.stroke()
  })
}