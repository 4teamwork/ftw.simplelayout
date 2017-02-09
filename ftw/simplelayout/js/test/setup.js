import EventEmitter from "simplelayout/EventEmitter";

const EE = EventEmitter.getInstance();

chai.config.truncateThreshold = 0

beforeAll(() => {
  fixture.setBase('ftw/simplelayout/js/test/fixtures');
});

afterEach(function(){
  fixture.cleanup();
  EE.clean();
});
