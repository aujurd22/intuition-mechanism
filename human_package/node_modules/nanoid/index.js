import { urlAlphabet } from './url-alphabet/index.js'

export { urlAlphabet }

const GET_RANDOM_LIMIT = 65536

function fillRandom(buffer) {
  let from = 0
  while (from < buffer.length) {
    let to = Math.min(from + GET_RANDOM_LIMIT, buffer.length)
    crypto.getRandomValues(buffer.subarray(from, to))
    from = to
  }
}

export function random(bytes) {
  bytes |= 0
  if (bytes < 0) throw new RangeError('Wrong ID size')
  let buffer = Buffer.allocUnsafe(bytes)
  fillRandom(buffer)
  return buffer
}

export function customRandom(alphabet, defaultSize, getRandom) {
  let safeByteCutoff = 256 - (256 % alphabet.length)

  if (safeByteCutoff === 256) {
    let mask = alphabet.length - 1

    return (size = defaultSize) => {
      if (!size) return ''
      let id = ''
      while (true) {
        let bytes = getRandom(size)
        let i = size
        while (i--) {
          id += alphabet[bytes[i] & mask]
          if (id.length >= size) return id
        }
      }
    }
  }

  let step = Math.ceil((1.6 * 256 * defaultSize) / safeByteCutoff)

  return (size = defaultSize) => {
    if (!size) return ''
    let id = ''
    while (true) {
      let bytes = getRandom(step)
      let i = step
      while (i--) {
        if (bytes[i] < safeByteCutoff) {
          id += alphabet[bytes[i] % alphabet.length]
          if (id.length >= size) return id
        }
      }
    }
  }
}


const POOL_MAX = GET_RANDOM_LIMIT / 2

export function customAlphabet(alphabet, defaultSize = 21) {
  if (
    typeof alphabet !== 'string' ||
    !alphabet ||
    alphabet.length > 256
  ) {
    return customRandom(alphabet, defaultSize, random)
  }
  for (let i = 0; i < alphabet.length; i++) {
    if (alphabet.charCodeAt(i) > 255) {
      return customRandom(alphabet, defaultSize, random)
    }
  }

  let charCodes = Uint8Array.from(alphabet, str => {
    return str.charCodeAt(0)
  })
  let alphabetLen = alphabet.length
  let mask = (2 << (31 - Math.clz32((alphabetLen - 1) | 1))) - 1

  let pool = ''
  let poolOffset = 0
  let poolNext = 0

  return (size = defaultSize) => {
    size |= 0
    if (size < 0) throw new RangeError('Wrong ID size')
    if (size === 0) return ''
    if (poolOffset + size > pool.length) {
      let target = Math.max(poolNext, size)
      poolNext = Math.min(target * 16, POOL_MAX)
      let buffer = Buffer.allocUnsafe(target)
      if (mask === alphabetLen - 1) {
        fillRandom(buffer)
        for (let i = 0; i < target; i++) {
          buffer[i] = charCodes[buffer[i] & mask]
        }
      } else {
        let randomBytes = Buffer.allocUnsafe(
          Math.ceil((1.6 * (mask + 1) * target) / alphabetLen)
        )
        let accepted = 0
        while (accepted < target) {
          fillRandom(randomBytes)
          for (let i = 0; i < randomBytes.length; i++) {
            let index = randomBytes[i] & mask
            if (index < alphabetLen) {
              buffer[accepted++] = charCodes[index]
              if (accepted === target) break
            }
          }
        }
      }
      pool = buffer.toString('latin1')
      poolOffset = 0
    }
    poolOffset += size
    return pool.substring(poolOffset - size, poolOffset)
  }
}

export const nanoid = customAlphabet(urlAlphabet)
