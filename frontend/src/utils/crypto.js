import CryptoJS from 'crypto-js'

const SECRET_KEY = 'FastAPI2026SecureKey!@#$'

/**
 * 将密钥补齐到 32 字节，与后端 Python 的 ljust(32, b'\0') 一致
 */
function getKey() {
  const src = CryptoJS.enc.Utf8.parse(SECRET_KEY)
  // 提取原始字节
  const bytes = []
  for (let i = 0; i < src.sigBytes; i++) {
    bytes.push((src.words[i >>> 2] >>> (24 - (i % 4) * 8)) & 0xff)
  }
  // 补零到 32 字节
  while (bytes.length < 32) bytes.push(0)
  // 重建 WordArray
  const words = []
  for (let i = 0; i < 32; i += 4) {
    words.push((bytes[i] << 24) | (bytes[i + 1] << 16) | (bytes[i + 2] << 8) | bytes[i + 3])
  }
  return CryptoJS.lib.WordArray.create(words, 32)
}

/**
 * 解密后端返回的 AES-CBC 密文
 * 密文格式: base64(IV[16字节] + ciphertext)
 */
export function decrypt(encryptedBase64) {
  const raw = CryptoJS.enc.Base64.parse(encryptedBase64)

  // 前 16 字节 = IV，剩余 = 密文
  const ivWords = raw.words.slice(0, 4)
  const ctWords = raw.words.slice(4)
  const iv = CryptoJS.lib.WordArray.create(ivWords, 16)
  const ciphertext = CryptoJS.lib.WordArray.create(ctWords, raw.sigBytes - 16)

  const decrypted = CryptoJS.AES.decrypt(
    { ciphertext },
    getKey(),
    { iv, mode: CryptoJS.mode.CBC, padding: CryptoJS.pad.Pkcs7 }
  )

  return decrypted.toString(CryptoJS.enc.Utf8)
}
