/**
 * Unix タイムスタンプ (秒) を "2026/01/01 00:00" のような文字列に変換する
 */
export function formatUnixTimestamp(unixSeconds: number): string {
  return new Date(unixSeconds * 1000).toLocaleString("ja-JP", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}
