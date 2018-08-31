import Element from 'simplelayout/Element'
import $ from 'jquery'

describe('element', function() {
  function isUUID(search) {
    return /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/.test(search)
  }

  it('creates element with given template', function() {
    let element = new Element('<p>{{name}}</p>')
    let jQueryElement = element.create({ name: 'James Bond' })

    let nodeProps = $.map(jQueryElement, function(node) {
      return { content: node.innerHTML, tagName: node.tagName }
    })

    assert.deepEqual(nodeProps, [{ content: 'James Bond', tagName: 'P' }])
  })

  it('element is enabled initially', function() {
    let element = new Element('<p></p>')
    let jQueryElement = element.create()
    assert.isTrue(element.enabled)
    assert.equal(jQueryElement[0].className, '')
  })

  it('element can get enabled and disabled', function() {
    let element = new Element('<p></p>')
    let jQueryElement = element.create()
    element.isEnabled(false)
    assert.isFalse(element.enabled, 'Element should be disabled')
    assert.equal(jQueryElement[0].className, 'disabled')
    element.isEnabled(true)
    assert.isTrue(element.enabled, 'Element should be enabled')
    assert.equal(jQueryElement[0].className, '')
  })

  it('element can store data', function() {
    let element = new Element('<p></p>')
    let jQueryElement = element.create()
    jQueryElement.data({ name: 'James Bond' })

    assert.equal(jQueryElement.data('name'), 'James Bond')
    assert.equal(jQueryElement.data().object.id, element.id)
  })

  it('can get data from element', function() {
    let element = new Element(`<p data-name='{{name}}'></p>`)
    let jQueryElement = element.create({ name: 'James Bond' })

    assert.equal(jQueryElement.data('name'), 'James Bond')
  })

  it('element has UUID on create', function() {
    let element = new Element('<p></p>')
    let jQueryElement = element.create('')

    let uuid = jQueryElement.data('id')

    assert(isUUID(uuid), 'Element has not a correct UUID')
  })

  it('element extends given data', function() {
    let element = new Element('<p></p>')
    element.create()
    element.data({ name: 'James Bond' })
    element.data({ code: '007' })

    assert.equal(element.data().name, 'James Bond')
    assert.equal(element.data().code, '007')
    assert.equal(element.data().object, element)
  })

  it('can remove or detach the element', function() {
    let element = new Element('<p></p>')
    element.create('')
    let target = $('<div>')
    target.append(element.element)
    element.remove()
    assert.equal(target.children().length, 0, 'The block element has not been deleted')
    target.append(element.element)
    assert.equal(target.children().length, 1, 'The block element has been removed')
    element.detach()
    assert.equal(target.children().length, 0, 'The block element has not been detached')
  })
})
