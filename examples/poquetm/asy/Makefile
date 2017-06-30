PDF= one_job.pdf one_job_context.pdf workload_example.pdf gantt_easy.pdf gantt_offline.pdf gantt_switch_off.pdf easy_bf0.pdf easy_bf1.pdf easy_bf1_rel.pdf easy_bf2.pdf easy_bf2_rel.pdf easy_bf3.pdf easy_bf3_rel.pdf easy_bf4.pdf easy_bf4_pre.pdf easy_bf5.pdf easy_bf6.pdf llh_visualised.pdf llh_previsional_schedule.pdf
PNG=$(PDF:.pdf=.png)

# Disables parallel builds (does not work in this case)
.NOTPARALLEL:

pdf: $(PDF)
png: $(PNG)

one_job.pdf: job_figures.asy
	asy $<
one_job_context.pdf: job_figures.asy
	asy $<

workload_example.pdf: gantt_examples.asy
	asy $<
gantt_easy.pdf: gantt_examples.asy
	asy $<
gantt_offline.pdf: gantt_examples.asy
	asy $<
gantt_switch_off.pdf: gantt_examples.asy
	asy $<

easy_bf0.pdf: easy_bf.asy
	asy $<
easy_bf1.pdf: easy_bf.asy
	asy $<
easy_bf1_rel.pdf: easy_bf.asy
	asy $<
easy_bf2.pdf: easy_bf.asy
	asy $<
easy_bf2_rel.pdf: easy_bf.asy
	asy $<
easy_bf3.pdf: easy_bf.asy
	asy $<
easy_bf3_rel.pdf: easy_bf.asy
	asy $<
easy_bf4.pdf: easy_bf.asy
	asy $<
easy_bf5.pdf: easy_bf.asy
	asy $<
easy_bf6.pdf: easy_bf.asy
	asy $<

llh_visualised.pdf: llh.asy
	asy $<
llh_previsional_schedule.pdf: llh.asy
	asy $<

%.png: %.pdf
	inkscape -e $@ $^ -b "#ffffff"

make clean:
	rm -f $(PDF) $(PNG)
