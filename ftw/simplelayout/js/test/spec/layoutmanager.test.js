import Layoutmanager from 'simplelayout/Layoutmanager'
import $ from 'jquery'

describe('Layoutmanager', function() {
  let layoutmanager
  let target

  beforeEach(function() {
    layoutmanager = new Layoutmanager()
    target = $('<div></div>')
    layoutmanager.attachTo(target)
  })

  it('is a constructor function', function() {
    assert.throw(
      Layoutmanager,
      TypeError,
      'Layoutmanager constructor cannot be called as a function.'
    )
  })

  it('can be added to a target node.', function() {
    let addedNodes = $.map(target.children(), function(e) {
      return [{ tag: e.tagName, classes: e.className }]
    })

    assert.deepEqual(addedNodes, [{ tag: 'DIV', classes: 'sl-simplelayout' }])
  })

  it('hasLayouts returns true if layouts are inserted', function() {
    assert.isFalse(layoutmanager.hasLayouts(), 'Should have no layouts inserted')

    layoutmanager.insertLayout()

    assert.isTrue(layoutmanager.hasLayouts(), 'Should have layouts inserted')
  })

  it('can get inserted and committed layouts', function() {
    let layout2 = layoutmanager.insertLayout()
    layoutmanager.insertLayout()
    layoutmanager.insertLayout()
    let layouts = $.map(layoutmanager.getCommittedLayouts(), function(block) {
      return block.committed
    })
    assert.deepEqual(layouts, [])
    layout2.commit()
    layouts = $.map(layoutmanager.getCommittedLayouts(), function(block) {
      return block.committed
    })
    assert.deepEqual(layouts, [true])
  })

  describe('Layout-transactions', function() {
    it('can insert a Layout.', function() {
      layoutmanager.insertLayout()

      let addedNodes = $.map(layoutmanager.layouts, function(e) {
        return e.committed
      })

      assert.deepEqual(addedNodes, [false])
    })

    it('can delete a Layout.', function() {
      let layout = layoutmanager.insertLayout()
      layoutmanager.deleteLayout(layout.id)

      let addedNodes = $.map(target.find('.sl-layout'), function(e) {
        return { tag: e.tagName, classes: e.className }
      })

      assert.deepEqual(addedNodes, [])
    })

    it('layout stores parent information', function() {
      let generatedLayout = layoutmanager.insertLayout()
      assert.equal(layoutmanager.id, generatedLayout.parent.id, 'Should store parent id')
    })

    it('layout can remove hinself from manager', function() {
      let generatedLayout = layoutmanager.insertLayout()
      generatedLayout.delete()

      assert.deepEqual(
        $.map(layoutmanager.layouts, function(layout) {
          return layout.id
        }),
        []
      )
    })

    it('can move a block', function() {
      let layout1 = layoutmanager.insertLayout().commit()
      let layout2 = layoutmanager.insertLayout().commit()
      let generatedBlock = layout1.insertBlock().commit()

      layoutmanager.moveBlock(generatedBlock, layout2)

      assert.equal(layout1.getCommittedBlocks(), 0, 'Should have no blocks on source layout')
      assert.deepEqual(
        $.map(layout2.getCommittedBlocks(), function(block) {
          return { id: block.id, committed: block.committed, parent: block.parent.id }
        }),
        [{ id: generatedBlock.id, committed: generatedBlock.committed, parent: layout2.id }]
      )
    })

    it('can get inserted and committed blocks', function() {
      let layout1 = layoutmanager.insertLayout().commit()
      let layout2 = layoutmanager.insertLayout().commit()
      let block1 = layout1.insertBlock()
      let block2 = layout2.insertBlock()
      assert.deepEqual(
        [false, false],
        $.map(layoutmanager.getInsertedBlocks(), function(block) {
          return block.committed
        }),
        'should have two inserted blocks.'
      )

      assert.deepEqual(
        [],
        $.map(layoutmanager.getCommittedBlocks(), function(block) {
          return block.committed
        }),
        'all blocks should be inserted.'
      )

      block1.commit()
      block2.commit()

      assert.deepEqual(
        [true, true],
        $.map(layoutmanager.getCommittedBlocks(), function(block) {
          return block.committed
        }),
        'should have two committed blocks'
      )

      assert.deepEqual(
        [],
        $.map(layoutmanager.getInsertedBlocks(), function(block) {
          return block.committed
        }),
        'all blocks should be committed.'
      )
    })
  })
})
