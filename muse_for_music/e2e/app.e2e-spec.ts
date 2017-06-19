import { Muse4musicUiPage } from './app.po';

describe('muse4music-ui App', () => {
  let page: Muse4musicUiPage;

  beforeEach(() => {
    page = new Muse4musicUiPage();
  });

  it('should display welcome message', done => {
    page.navigateTo();
    page.getParagraphText()
      .then(msg => expect(msg).toEqual('Welcome to app!!'))
      .then(done, done.fail);
  });
});
