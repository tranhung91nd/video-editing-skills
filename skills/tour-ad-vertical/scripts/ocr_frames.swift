import Foundation
import Vision
import AppKit

// usage: ocr_frames <dir>  -> prints "<file>\t<text joined by |>" for each jpg
let dir = CommandLine.arguments[1]
let files = (try FileManager.default.contentsOfDirectory(atPath: dir)).filter { $0.hasSuffix(".jpg") }.sorted()
for f in files {
    let url = URL(fileURLWithPath: dir).appendingPathComponent(f)
    guard let img = NSImage(contentsOf: url), let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { continue }
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.usesLanguageCorrection = false
    try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
    let texts = (req.results ?? []).compactMap { o -> String? in
        guard let c = o.topCandidates(1).first, c.confidence > 0.3 else { return nil }
        let b = o.boundingBox
        return "\(c.string)@\(String(format: "%.2f,%.2f", b.midX, 1 - b.midY))"
    }
    print("\(f)\t\(texts.joined(separator: " | "))")
}
