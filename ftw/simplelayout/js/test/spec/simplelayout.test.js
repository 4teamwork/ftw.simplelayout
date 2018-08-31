import Simplelayout from 'simplelayout/Simplelayout'
import $ from 'jquery'

describe('Simplelayout', function() {
  let simplelayout

  beforeEach(function() {
    simplelayout = new Simplelayout()
  })

  it('is a constructor function', function() {
    assert.throw(
      Simplelayout,
      TypeError,
      'Simplelayout constructor cannot be called as a function.'
    )
  })

  it('can insert a manager', function() {
    let generatedManager = simplelayout.insertManager()
    assert.deepEqual(
      $.map(simplelayout.managers, function(manager) {
        return { id: manager.id }
      }),
      [{ id: generatedManager.id }]
    )
  })

  it('can manage restrictions for given layout', function() {
    let testStructure = fixture.load('simplelayout.html')
    let simplelayout2 = new Simplelayout()
    simplelayout2.restore($(testStructure))
    let managers = $.map(simplelayout2.managers, function(manager) {
      return manager
    })
    let manager1 = managers[0]
    let manager2 = managers[1]
    simplelayout2.options.layoutRestrictions = {
      2: [manager1.id],
      4: [manager2.id]
    }

    simplelayout2.restrictLayout(2)
    assert.deepEqual(
      $.map(simplelayout2.managers, function(manager) {
        return manager.enabled
      }),
      [false, true]
    )

    simplelayout2.restrictLayout(4)
    simplelayout2.restrictLayout(2)
    assert.deepEqual(
      $.map(simplelayout2.managers, function(manager) {
        return manager.enabled
      }),
      [false, false]
    )

    simplelayout2.allowLayout(4)
    assert.deepEqual(
      $.map(simplelayout2.managers, function(manager) {
        return manager.enabled
      }),
      [false, true]
    )

    simplelayout2.allowLayout(2)
    assert.deepEqual(
      $.map(simplelayout2.managers, function(manager) {
        return manager.enabled
      }),
      [true, true]
    )
  })

  describe('Element transactions', function() {
    it('can move a layout', function() {
      let manager1 = simplelayout.insertManager()
      let manager2 = simplelayout.insertManager()

      let layout1 = manager1.insertLayout().commit()
      let layout2 = manager1.insertLayout().commit()
      let layout3 = manager2.insertLayout().commit()

      simplelayout.moveLayout(layout1, manager2)

      assert.deepEqual(
        $.map(manager1.layouts, function(layout) {
          return { id: layout.id, committed: layout.committed }
        }),
        [{ id: layout2.id, committed: true }]
      )

      assert.deepEqual(
        $.map(manager2.layouts, function(layout) {
          return { id: layout.id, committed: layout.committed, data: layout.data() }
        }),
        [
          { id: layout3.id, committed: true, data: layout3.data() },
          { id: layout1.id, committed: true, data: layout1.data() }
        ]
      )
    })
  })

  it('can get committed blocks', function() {
    let manager1 = simplelayout.insertManager()
    let layout1 = manager1.insertLayout()
    let generatedBlock = layout1.insertBlock('<p></p>', 'textblock')

    assert.deepEqual(
      [],
      $.map(simplelayout.getCommittedBlocks(), function(block) {
        return block.committed
      }),
      'should have no committed blocks.'
    )

    generatedBlock.commit()

    assert.deepEqual(
      [true],
      $.map(simplelayout.getCommittedBlocks(), function(block) {
        return block.committed
      }),
      'should have one committed blocks.'
    )
  })

  it('can get inserted blocks', function() {
    let manager1 = simplelayout.insertManager()
    let layout1 = manager1.insertLayout()
    let generatedBlock = layout1.insertBlock('<p></p>', 'textblock')

    assert.deepEqual(
      [false],
      $.map(simplelayout.getInsertedBlocks(), function(block) {
        return block.committed
      }),
      'should have one committed block.'
    )

    generatedBlock.commit()

    assert.deepEqual(
      [],
      $.map(simplelayout.getInsertedBlocks(), function(block) {
        return block.committed
      }),
      'should have no inserted blocks.'
    )
  })

  it('can restore DOM structure', function() {
    fixture.load('simplelayout.html')
    simplelayout.restore($(fixture.el))
    let data = $.map(simplelayout.managers, function(manager) {
      return {
        committed: manager.committed,
        represents: manager.represents,
        layouts: $.map(manager.layouts, function(layout) {
          return {
            committed: layout.committed,
            columns: layout.columns,
            blocks: $.map(layout.blocks, function(block) {
              return {
                committed: block.committed,
                represents: block.represents,
                type: block.type
              }
            })
          }
        })
      }
    })
    assert.deepEqual(data, [
      {
        committed: true,
        represents: 'slot1',
        layouts: [
          {
            committed: true,
            columns: 4,
            blocks: [
              {
                committed: true,
                represents: 'c968b492-563a-11e5-885d-feff819cdc9f',
                type: 'textblock'
              },
              {
                committed: true,
                represents: 'c968b726-563a-11e5-885d-deff819cdc9f',
                type: 'textblock'
              }
            ]
          }
        ]
      },
      {
        committed: true,
        represents: 'slot2',
        layouts: [
          {
            committed: true,
            columns: 4,
            blocks: [
              {
                committed: true,
                represents: 'c968b816-563a-11e5-885d-feff819cd49f',
                type: 'textblock'
              },
              {
                committed: true,
                represents: 'c968b492-563a-11e5-885d-fedf819cdc9f',
                type: 'textblock'
              },
              {
                committed: true,
                represents: 'c968b492-563a-11e5-885d-feff8196dc9f',
                type: 'textblock'
              }
            ]
          }
        ]
      }
    ])
  })
})
