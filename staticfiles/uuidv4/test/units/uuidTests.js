'use strict';

const assert = require('assertthat');

const uuidv4 = require('../../src/uuidv4');

suite('uuidv4', () => {
  test('is a function', async () => {
    assert.that(uuidv4).is.ofType('function');
  });

  test('returns a v4 UUID.', async () => {
    const uuid = uuidv4();

    assert.that(uuid).is.ofType('string');
    assert.that(uuidv4.regex.v4.test(uuid)).is.true();
  });

  test('returns a different v4 UUID on each call.', async () => {
    const uuid = uuidv4(),
          uuidOther = uuidv4();

    assert.that(uuid).is.not.equalTo(uuidOther);
  });

  suite('regex', () => {
    test('is an object.', async () => {
      assert.that(uuidv4.regex).is.ofType('object');
    });

    suite('v4', () => {
      test('is a regular expression that describes a UUID v4.', async () => {
        assert.that(uuidv4.regex.v4).is.equalTo(/[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12}/);
      });
    });

    suite('v5', () => {
      test('is a regular expression that describes a UUID v5.', async () => {
        assert.that(uuidv4.regex.v5).is.equalTo(/[a-f0-9]{8}-[a-f0-9]{4}-5[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12}/);
      });
    });
  });

  suite('is', () => {
    test('returns false if value is missing.', async () => {
      assert.that(uuidv4.is()).is.false();
    });

    test('returns true if a UUID v4 is given.', async () => {
      assert.that(uuidv4.is('9afb733b-5001-4275-a099-03a1d2cca51e')).is.true();
    });

    test('returns true if a UUID v5 is given.', async () => {
      assert.that(uuidv4.is('cdb63720-9628-5ef6-bbca-2e5ce6094f3c')).is.true();
    });

    test('returns false if no UUID v4 or v5 is given.', async () => {
      assert.that(uuidv4.is('definitely-not-a-uuid')).is.false();
    });
  });

  suite('fromString', () => {
    test('is a function.', async () => {
      assert.that(uuidv4.fromString).is.ofType('function');
    });

    test('throws an error if no text is given.', async () => {
      assert.that(() => {
        uuidv4.fromString();
      }).is.throwing('Text is missing.');
    });

    test('returns a UUID v5 that is derived from the given text.', async () => {
      const uuid = uuidv4.fromString('the native web');

      assert.that(uuid).is.equalTo('cdb63720-9628-5ef6-bbca-2e5ce6094f3c');
      assert.that(uuidv4.regex.v5.test(uuid)).is.true();
    });
  });

  suite('empty', () => {
    test('is a function.', async () => {
      assert.that(uuidv4.empty).is.ofType('function');
    });

    test('returns 00000000-0000-0000-0000-000000000000.', async () => {
      assert.that(uuidv4.empty()).is.equalTo('00000000-0000-0000-0000-000000000000');
    });
  });
});
