import Handlebars from 'handlebars'

Handlebars.registerHelper('times', function(n, block) {
  let accum = ''
  for (let i = 0; i < n; i += 1) {
    accum += block.fn(i)
  }
  return accum
})

export default function handlebarsTimes() {}
